import { Html, OrbitControls } from "@react-three/drei";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import type { TranslationKey } from "../../i18n/i18n";
import type {
  EngineeringSceneModel,
  FlowSegment,
} from "./visualizationModel";
import {
  buildFlowSegments,
  solverToSceneVector,
} from "./visualizationModel";

export type CameraView = "isometric" | "front" | "side" | "top";

type T = (
  key: TranslationKey,
  values?: Record<string, string | number>,
) => string;

const toThree = (
  value: [number, number, number],
): [number, number, number] => solverToSceneVector(value);

export function EngineeringScene3D({
  model,
  cameraView,
  showAnnotations,
  showParticles,
  ductOpacity = 0.16,
  t,
}: {
  model: EngineeringSceneModel;
  cameraView: CameraView;
  showAnnotations: boolean;
  showParticles: boolean;
  ductOpacity?: number;
  t: T;
}) {
  const extent = Math.max(
    model.plenum.width,
    model.plenum.height,
    model.plenum.depth,
    model.ductVisual.length,
    1,
  );

  return (
    <div
      className="engineering-canvas"
      role="img"
      aria-label={t("engineeringSceneDescription")}
      data-testid="engineering-3d-scene"
    >
      <Canvas
        camera={{
          position: [extent * 1.35, extent, extent * 1.55],
          near: 0.01,
          far: extent * 30,
        }}
        dpr={[1, 1.75]}
        gl={{ antialias: true }}
      >
        <color attach="background" args={["#081211"]} />

        <ambientLight intensity={1.2} />

        <directionalLight
          position={[extent, extent * 1.4, extent]}
          intensity={2.2}
        />

        <SceneCamera view={cameraView} extent={extent} />

        <axesHelper args={[extent * 0.45]} />

        <Duct
  model={model}
  opacity={ductOpacity}
/>

        <Plenum model={model} />

        <Inlet
          model={model}
          showAnnotations={showAnnotations}
          t={t}
        />

        <OutletGrid
          model={model}
          showAnnotations={showAnnotations}
        />

        <Deflectors
          model={model}
          showAnnotations={showAnnotations}
        />

        {showParticles && model.hasSolverResult && (
          <FlowIndicators model={model} />
        )}

        <OrbitControls
          makeDefault
          enableDamping
          dampingFactor={0.08}
        />
      </Canvas>
    </div>
  );
}

function SceneCamera({
  view,
  extent,
}: {
  view: CameraView;
  extent: number;
}) {
  const { camera, controls } = useThree();

  useEffect(() => {
    const positions: Record<
      CameraView,
      [number, number, number]
    > = {
      isometric: [
        extent * 1.35,
        extent,
        extent * 1.55,
      ],

      front: [
        0,
        0,
        -extent * 2.4,
      ],

      side: [
        extent * 2.4,
        0,
        extent * 0.5,
      ],

      top: [
        0,
        extent * 2.4,
        extent * 0.5,
      ],
    };

    camera.position.set(...positions[view]);
    camera.up.set(0, 1, 0);
    camera.lookAt(0, extent * 0.5, 0);
    camera.updateProjectionMatrix();

    const orbit = controls as {
      target?: THREE.Vector3;
      update?: () => void;
    } | null;

    orbit?.target?.set(0, extent * 0.5, 0);
    orbit?.update?.();
  }, [camera, controls, extent, view]);

  return null;
}

function Duct({
  model,
  opacity,
}: {
  model: EngineeringSceneModel;
  opacity: number;
}) {
  const endPosition = useMemo(
    () =>
      new THREE.Vector3(
        ...toThree(model.ductVisual.endPosition),
      ),
    [model.ductVisual.endPosition],
  );

  const direction = useMemo(() => {
    const vector = new THREE.Vector3(
      ...toThree(model.ductVisual.direction),
    );

    if (vector.lengthSq() > 0) {
      vector.normalize();
    }

    return vector;
  }, [model.ductVisual.direction]);

  const isCircular = useMemo(() => {
    const larger = Math.max(
      model.ductVisual.width,
      model.ductVisual.height,
      0.0001,
    );

    return (
      Math.abs(
        model.ductVisual.width -
          model.ductVisual.height,
      ) /
        larger <
      0.01
    );
  }, [
    model.ductVisual.height,
    model.ductVisual.width,
  ]);

  const dimensions = useMemo(() => {
    const width = model.ductVisual.width;
    const height = model.ductVisual.height;
    const length = model.ductVisual.length;
    const diameter = (width + height) / 2;
    const wallThickness = Math.max(
      Math.min(diameter, width, height) * 0.018,
      0.012,
    );
    const flangeDepth = Math.max(wallThickness * 2.4, 0.028);
    const flangeWidth = Math.max(wallThickness * 3.2, 0.045);

    return {
      width,
      height,
      length,
      diameter,
      wallThickness,
      flangeDepth,
      flangeWidth,
    };
  }, [
    model.ductVisual.height,
    model.ductVisual.length,
    model.ductVisual.width,
  ]);

  const outerGeometry = useMemo(() => {
    if (isCircular) {
      const cylinder = new THREE.CylinderGeometry(
        dimensions.diameter / 2,
        dimensions.diameter / 2,
        dimensions.length,
        128,
        1,
        true,
      );
      cylinder.rotateX(Math.PI / 2);
      return cylinder;
    }

    return new THREE.BoxGeometry(
      dimensions.width,
      dimensions.height,
      dimensions.length,
    );
  }, [dimensions, isCircular]);

  const innerGeometry = useMemo(() => {
    if (isCircular) {
      const innerDiameter = Math.max(
        dimensions.diameter -
          dimensions.wallThickness * 2,
        dimensions.diameter * 0.88,
      );
      const cylinder = new THREE.CylinderGeometry(
        innerDiameter / 2,
        innerDiameter / 2,
        dimensions.length * 0.995,
        128,
        1,
        true,
      );
      cylinder.rotateX(Math.PI / 2);
      return cylinder;
    }

    return new THREE.BoxGeometry(
      Math.max(
        dimensions.width -
          dimensions.wallThickness * 2,
        dimensions.width * 0.9,
      ),
      Math.max(
        dimensions.height -
          dimensions.wallThickness * 2,
        dimensions.height * 0.9,
      ),
      dimensions.length * 0.995,
    );
  }, [dimensions, isCircular]);

  useEffect(() => {
    return () => {
      outerGeometry.dispose();
      innerGeometry.dispose();
    };
  }, [innerGeometry, outerGeometry]);

  if (direction.lengthSq() === 0) {
    return null;
  }

  const center = endPosition
    .clone()
    .addScaledVector(
      direction,
      -dimensions.length / 2,
    );

  const quaternion =
    new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 0, 1),
      direction,
    );

  const clampedOpacity = THREE.MathUtils.clamp(
    opacity,
    0.04,
    1,
  );

  const edgeOpacity = THREE.MathUtils.clamp(
    0.45 + (1 - clampedOpacity) * 0.4,
    0.45,
    0.9,
  );

  return (
    <group
      position={center.toArray()}
      quaternion={quaternion}
    >
      <mesh geometry={outerGeometry}>
        <meshStandardMaterial
          color="#7f918d"
          metalness={0.78}
          roughness={0.34}
          transparent={clampedOpacity < 1}
          opacity={clampedOpacity}
          side={THREE.DoubleSide}
          depthWrite={clampedOpacity > 0.45}
        />
      </mesh>

      <mesh geometry={innerGeometry} scale={[0.995, 0.995, 0.995]}>
        <meshStandardMaterial
          color="#1a2926"
          metalness={0.42}
          roughness={0.62}
          transparent
          opacity={Math.max(clampedOpacity * 0.45, 0.035)}
          side={THREE.BackSide}
          depthWrite={false}
        />
      </mesh>

      <lineSegments>
        <edgesGeometry args={[outerGeometry]} />
        <lineBasicMaterial
          color="#b7ccc7"
          transparent
          opacity={edgeOpacity}
        />
      </lineSegments>

      {isCircular ? (
        <>
          <DuctFlange
            diameter={dimensions.diameter}
            tube={dimensions.flangeWidth}
            positionZ={-dimensions.length / 2}
            depth={dimensions.flangeDepth}
            opacity={clampedOpacity}
          />
          <DuctFlange
            diameter={dimensions.diameter}
            tube={dimensions.flangeWidth}
            positionZ={dimensions.length / 2}
            depth={dimensions.flangeDepth}
            opacity={clampedOpacity}
          />
        </>
      ) : (
        <>
          <RectangularDuctFlange
            width={dimensions.width}
            height={dimensions.height}
            thickness={dimensions.flangeWidth}
            depth={dimensions.flangeDepth}
            positionZ={-dimensions.length / 2}
            opacity={clampedOpacity}
          />
          <RectangularDuctFlange
            width={dimensions.width}
            height={dimensions.height}
            thickness={dimensions.flangeWidth}
            depth={dimensions.flangeDepth}
            positionZ={dimensions.length / 2}
            opacity={clampedOpacity}
          />
        </>
      )}
    </group>
  );
}

function DuctFlange({
  diameter,
  tube,
  positionZ,
  depth,
  opacity,
}: {
  diameter: number;
  tube: number;
  positionZ: number;
  depth: number;
  opacity: number;
}) {
  return (
    <group position={[0, 0, positionZ]}>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry
          args={[
            diameter / 2 + tube * 0.42,
            tube / 2,
            16,
            128,
          ]}
        />
        <meshStandardMaterial
          color="#a9bbb7"
          metalness={0.86}
          roughness={0.26}
          transparent={opacity < 1}
          opacity={Math.max(opacity, 0.24)}
        />
      </mesh>

      <mesh
        position={[0, 0, depth / 2]}
        rotation={[Math.PI / 2, 0, 0]}
      >
        <cylinderGeometry
          args={[
            diameter / 2 + tube * 0.5,
            diameter / 2 + tube * 0.5,
            depth,
            128,
            1,
            true,
          ]}
        />
        <meshStandardMaterial
          color="#889b97"
          metalness={0.82}
          roughness={0.3}
          transparent
          opacity={Math.max(opacity * 0.8, 0.18)}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
}

function RectangularDuctFlange({
  width,
  height,
  thickness,
  depth,
  positionZ,
  opacity,
}: {
  width: number;
  height: number;
  thickness: number;
  depth: number;
  positionZ: number;
  opacity: number;
}) {
  const material = (
    <meshStandardMaterial
      color="#a9bbb7"
      metalness={0.86}
      roughness={0.26}
      transparent={opacity < 1}
      opacity={Math.max(opacity, 0.24)}
    />
  );

  return (
    <group position={[0, 0, positionZ]}>
      <mesh position={[0, height / 2, 0]}>
        <boxGeometry
          args={[
            width + thickness * 2,
            thickness,
            depth,
          ]}
        />
        {material}
      </mesh>
      <mesh position={[0, -height / 2, 0]}>
        <boxGeometry
          args={[
            width + thickness * 2,
            thickness,
            depth,
          ]}
        />
        {material}
      </mesh>
      <mesh position={[width / 2, 0, 0]}>
        <boxGeometry args={[thickness, height, depth]} />
        {material}
      </mesh>
      <mesh position={[-width / 2, 0, 0]}>
        <boxGeometry args={[thickness, height, depth]} />
        {material}
      </mesh>
    </group>
  );
}

function Plenum({
  model,
}: {
  model: EngineeringSceneModel;
}) {
  const {
    width,
    height,
    depth,
  } = model.plenum;

  return (
    <group position={[0, depth / 2, 0]}>
      <mesh>
        <boxGeometry args={[width, depth, height]} />

        <meshStandardMaterial
          color="#38554f"
          transparent
          opacity={0.12}
          side={THREE.DoubleSide}
        />
      </mesh>

      <lineSegments>
        <edgesGeometry
          args={[
            new THREE.BoxGeometry(
              width,
              depth,
              height,
            ),
          ]}
        />

        <lineBasicMaterial color="#71988f" />
      </lineSegments>
    </group>
  );
}

function Inlet({
  model,
  showAnnotations,
  t,
}: {
  model: EngineeringSceneModel;
  showAnnotations: boolean;
  t: T;
}) {
  const inlet = model.inlet;

  const arrowLength = Math.max(
    model.plenum.depth * 0.24,
    0.2,
  );

  const position = toThree(inlet.position);
  const direction = toThree(inlet.direction);

  return (
    <group>
      <mesh position={position}>
        <sphereGeometry
          args={[
            Math.max(
              Math.min(
                inlet.width,
                inlet.height,
              ) * 0.18,
              0.04,
            ),
            16,
            12,
          ]}
        />

        <meshStandardMaterial
          color="#6dd9cf"
          emissive="#214d48"
        />
      </mesh>

      {Math.hypot(...direction) > 0 && (
        <arrowHelper
          args={[
            new THREE.Vector3(...direction),
            new THREE.Vector3(...position),
            arrowLength,
            0x6dd9cf,
            arrowLength * 0.22,
            arrowLength * 0.12,
          ]}
        />
      )}

      {showAnnotations && (
        <Html
          position={[
            position[0],
            position[1] + inlet.height * 0.35,
            position[2],
          ]}
          center
        >
          <span className="scene-label">
            {t("inlet")}

            <small>
              (
              {inlet.direction
                .map(value => value.toFixed(3))
                .join(", ")}
              )
            </small>
          </span>
        </Html>
      )}
    </group>
  );
}

function OutletGrid({
  model,
  showAnnotations,
}: {
  model: EngineeringSceneModel;
  showAnnotations: boolean;
}) {
  return (
    <group>
      {model.outlets.map(outlet => {
        const color =
          outlet.heat === null
            ? new THREE.Color("#25413b")
            : new THREE.Color().setHSL(
                0.46 - outlet.heat * 0.28,
                0.68,
                0.28 + outlet.heat * 0.24,
              );

        return (
          <group
            key={outlet.id}
            position={toThree(outlet.position)}
          >
            <DualAxisOutletLouver
              width={outlet.width}
              height={outlet.height}
              color={color}
            />

            {showAnnotations && (
              <Html
                position={[0, -0.085, 0]}
                center
              >
                <span className="scene-label outlet-label">
                  {outlet.id}

                  {outlet.value?.value !== null &&
                  outlet.value ? (
                    <small>
                      {outlet.value.value.toFixed(3)}{" "}
                      {outlet.value.unit}
                    </small>
                  ) : null}
                </span>
              </Html>
            )}
          </group>
        );
      })}
    </group>
  );
}

function DualAxisOutletLouver({
  width,
  height,
  color,
}: {
  width: number;
  height: number;
  color: THREE.Color;
}) {
  const grilleDepth = 0.15;
  const frameThickness = Math.max(
    Math.min(width, height) * 0.045,
    0.008,
  );
  const bladeThickness = Math.max(
    frameThickness * 0.42,
    0.004,
  );
  const frontY = -grilleDepth / 2;
  const rearY = grilleDepth / 2;
  const verticalLayerY = -grilleDepth * 0.18;
  const horizontalLayerY = grilleDepth * 0.18;

  return (
    <group>
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[width, grilleDepth, height]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={0.16}
          emissive={color}
          emissiveIntensity={0.1}
          side={THREE.DoubleSide}
        />
      </mesh>

      <OutletFrame
        width={width}
        height={height}
        thickness={frameThickness}
        depth={Math.max(frameThickness * 0.9, 0.012)}
        y={frontY}
      />

      <OutletFrame
        width={width}
        height={height}
        thickness={frameThickness}
        depth={Math.max(frameThickness * 0.75, 0.01)}
        y={rearY}
      />

      <OutletSideWalls
        width={width}
        height={height}
        depth={grilleDepth}
        thickness={Math.max(frameThickness * 0.45, 0.006)}
      />

      <VerticalChevronLayer
        width={width}
        height={height}
        bladeThickness={bladeThickness}
        y={verticalLayerY}
        bladeDepth={grilleDepth * 0.34}
      />

      <HorizontalChevronLayer
        width={width}
        height={height}
        bladeThickness={bladeThickness}
        y={horizontalLayerY}
        bladeDepth={grilleDepth * 0.34}
      />
    </group>
  );
}

function OutletFrame({
  width,
  height,
  thickness,
  depth,
  y,
}: {
  width: number;
  height: number;
  thickness: number;
  depth: number;
  y: number;
}) {
  return (
    <group position={[0, y, 0]}>
      <LouverBar
        size={[width, depth, thickness]}
        position={[0, 0, height / 2 - thickness / 2]}
      />
      <LouverBar
        size={[width, depth, thickness]}
        position={[0, 0, -height / 2 + thickness / 2]}
      />
      <LouverBar
        size={[thickness, depth, height]}
        position={[-width / 2 + thickness / 2, 0, 0]}
      />
      <LouverBar
        size={[thickness, depth, height]}
        position={[width / 2 - thickness / 2, 0, 0]}
      />
    </group>
  );
}

function OutletSideWalls({
  width,
  height,
  depth,
  thickness,
}: {
  width: number;
  height: number;
  depth: number;
  thickness: number;
}) {
  const innerWidth = Math.max(width - thickness * 2, width * 0.9);
  const innerHeight = Math.max(height - thickness * 2, height * 0.9);

  return (
    <group>
      <LouverBar
        size={[innerWidth, depth, thickness]}
        position={[0, 0, height / 2 - thickness / 2]}
      />
      <LouverBar
        size={[innerWidth, depth, thickness]}
        position={[0, 0, -height / 2 + thickness / 2]}
      />
      <LouverBar
        size={[thickness, depth, innerHeight]}
        position={[-width / 2 + thickness / 2, 0, 0]}
      />
      <LouverBar
        size={[thickness, depth, innerHeight]}
        position={[width / 2 - thickness / 2, 0, 0]}
      />
    </group>
  );
}

function VerticalChevronLayer({
  width,
  height,
  bladeThickness,
  y,
  bladeDepth,
}: {
  width: number;
  height: number;
  bladeThickness: number;
  y: number;
  bladeDepth: number;
}) {
  const count = 6;
  const usableWidth = width * 0.78;
  const bladeHeight = height * 0.78;
  const angle = THREE.MathUtils.degToRad(18);

  return (
    <group position={[0, y, 0]}>
      {Array.from({ length: count }, (_, index) => {
        const ratio = index / (count - 1);
        const x = -usableWidth / 2 + usableWidth * ratio;
        const rotation = x < 0 ? angle : -angle;

        return (
          <LouverBar
            key={`vertical-${index}`}
            size={[
              bladeThickness,
              bladeDepth,
              bladeHeight,
            ]}
            position={[x, 0, 0]}
            rotation={[0, 0, rotation]}
          />
        );
      })}
    </group>
  );
}

function HorizontalChevronLayer({
  width,
  height,
  bladeThickness,
  y,
  bladeDepth,
}: {
  width: number;
  height: number;
  bladeThickness: number;
  y: number;
  bladeDepth: number;
}) {
  const count = 4;
  const usableHeight = height * 0.66;
  const bladeWidth = width * 0.82;
  const angle = THREE.MathUtils.degToRad(18);

  return (
    <group position={[0, y, 0]}>
      {Array.from({ length: count }, (_, index) => {
        const ratio = index / (count - 1);
        const z = -usableHeight / 2 + usableHeight * ratio;
        const rotation = z < 0 ? -angle : angle;

        return (
          <LouverBar
            key={`horizontal-${index}`}
            size={[
              bladeWidth,
              bladeDepth,
              bladeThickness,
            ]}
            position={[0, 0, z]}
            rotation={[rotation, 0, 0]}
          />
        );
      })}
    </group>
  );
}

function LouverBar({
  size,
  position,
  rotation = [0, 0, 0],
}: {
  size: [number, number, number];
  position: [number, number, number];
  rotation?: [number, number, number];
}) {
  return (
    <mesh position={position} rotation={rotation}>
      <boxGeometry args={size} />
      <meshStandardMaterial
        color="#9fb7b1"
        metalness={0.62}
        roughness={0.34}
      />
    </mesh>
  );
}

function Deflectors({
  model,
  showAnnotations,
}: {
  model: EngineeringSceneModel;
  showAnnotations: boolean;
}) {
  return (
    <group>
      {model.deflectors.map(
        (deflector, index) => (
          <group
            key={
              deflector.identifier || index
            }
            position={toThree([
              deflector.position_m.x,
              deflector.position_m.y,
              deflector.position_m.z,
            ])}
            rotation={[
              0,
              0,
              THREE.MathUtils.degToRad(
                deflector.angle_deg_about_y,
              ),
            ]}
          >
            <mesh>
              <boxGeometry
                args={[
                  deflector.width_m,
                  Math.max(
                    Math.min(
                      deflector.width_m,
                      deflector.height_m,
                    ) * 0.035,
                    0.004,
                  ),
                  deflector.height_m,
                ]}
              />

              <meshStandardMaterial
                color="#d8ff4f"
                metalness={0.55}
                roughness={0.38}
              />
            </mesh>

            {showAnnotations && (
              <Html
                position={[
                  0,
                  0,
                  deflector.height_m * 0.7,
                ]}
                center
              >
                <span className="scene-label deflector-label">
                  {deflector.identifier} ·{" "}
                  {deflector.angle_deg_about_y}°
                </span>
              </Html>
            )}
          </group>
        ),
      )}
    </group>
  );
}

function FlowIndicators({
  model,
}: {
  model: EngineeringSceneModel;
}) {
  const segments = buildFlowSegments(model);

  return (
    <group>
      {segments.map(segment => (
        <LinearParticles
          key={segment.id}
          segment={segment}
        />
      ))}
    </group>
  );
}

function LinearParticles({
  segment,
}: {
  segment: FlowSegment;
}) {
  const refs = useRef<THREE.Mesh[]>([]);

  const startVector = useMemo(
    () => new THREE.Vector3(...segment.start),
    [segment.start],
  );

  const directionVector = useMemo(() => {
    const vector = new THREE.Vector3(
      ...segment.direction,
    );

    if (vector.lengthSq() > 0) {
      vector.normalize();
    }

    return vector;
  }, [segment.direction]);

  const particleQuaternion = useMemo(() => {
    if (directionVector.lengthSq() === 0) {
      return new THREE.Quaternion();
    }

    return new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 0, 1),
      directionVector,
    );
  }, [directionVector]);

  useFrame(({ clock }) => {
    const normalizedSpeed =
      Math.max(segment.engineeringSpeed, 0) *
      (segment.kind === "duct" ? 0.015 : 0.055);

    refs.current.forEach(
      (mesh, index) => {
        const phase =
          (clock.elapsedTime *
            normalizedSpeed +
            index /
              Math.max(segment.count, 1)) %
          1;

        mesh.position
          .copy(startVector)
          .addScaledVector(
            directionVector,
            phase * segment.length,
          );
      },
    );
  });

  return (
    <group>
      {Array.from(
        { length: segment.count },
        (_, index) => (
          <mesh
            key={index}
            quaternion={particleQuaternion}
            scale={
              segment.kind === "duct"
                ? [1, 1, 2.2]
                : [0.78, 0.78, 4.8]
            }
            ref={mesh => {
              if (mesh) {
                refs.current[index] = mesh;
              }
            }}
          >
            <sphereGeometry
              args={[
                segment.kind === "duct"
                  ? 0.018
                  : 0.014,
                10,
                10,
              ]}
            />

            <meshBasicMaterial
              color={segment.color}
              transparent
              opacity={
                segment.kind === "duct"
                  ? 0.76
                  : 0.72
              }
            />
          </mesh>
        ),
      )}
    </group>
  );
}