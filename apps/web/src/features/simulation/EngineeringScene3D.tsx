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
  t,
}: {
  model: EngineeringSceneModel;
  cameraView: CameraView;
  showAnnotations: boolean;
  showParticles: boolean;
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

        <Duct model={model} />

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
}: {
  model: EngineeringSceneModel;
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

  const geometry = useMemo(() => {
    if (isCircular) {
      const diameter =
        (model.ductVisual.width +
          model.ductVisual.height) /
        2;

      const cylinder = new THREE.CylinderGeometry(
        diameter / 2,
        diameter / 2,
        model.ductVisual.length,
        64,
        1,
        true,
      );

      // CylinderGeometry is created along +Y. Rotate it so the
      // local duct axis is +Z, matching the rectangular version.
      cylinder.rotateX(Math.PI / 2);
      return cylinder;
    }

    return new THREE.BoxGeometry(
      model.ductVisual.width,
      model.ductVisual.height,
      model.ductVisual.length,
    );
  }, [
    isCircular,
    model.ductVisual.height,
    model.ductVisual.length,
    model.ductVisual.width,
  ]);

  useEffect(() => {
    return () => {
      geometry.dispose();
    };
  }, [geometry]);

  if (direction.lengthSq() === 0) {
    return null;
  }

  const center = endPosition
    .clone()
    .addScaledVector(
      direction,
      -model.ductVisual.length / 2,
    );

  const quaternion =
    new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 0, 1),
      direction,
    );

  return (
    <group
      position={center.toArray()}
      quaternion={quaternion}
    >
      <mesh geometry={geometry}>
        <meshStandardMaterial
          color="#304944"
          transparent
          opacity={0.1}
          side={THREE.DoubleSide}
        />
      </mesh>

      <lineSegments>
        <edgesGeometry args={[geometry]} />
        <lineBasicMaterial color="#5f837b" />
      </lineSegments>
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
  const frameThickness = Math.max(
    Math.min(width, height) * 0.045,
    0.008,
  );
  const bladeThickness = Math.max(
    frameThickness * 0.42,
    0.004,
  );
  const layerGap = Math.max(
    Math.min(width, height) * 0.065,
    0.018,
  );

  return (
    <group>
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[width, 0.028, height]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={0.22}
          emissive={color}
          emissiveIntensity={0.12}
        />
      </mesh>

      <OutletFrame
        width={width}
        height={height}
        thickness={frameThickness}
      />

      <VerticalChevronLayer
        width={width}
        height={height}
        bladeThickness={bladeThickness}
        y={-layerGap / 2}
      />

      <HorizontalChevronLayer
        width={width}
        height={height}
        bladeThickness={bladeThickness}
        y={layerGap / 2}
      />
    </group>
  );
}

function OutletFrame({
  width,
  height,
  thickness,
}: {
  width: number;
  height: number;
  thickness: number;
}) {
  const depth = Math.max(thickness * 0.8, 0.008);

  return (
    <group>
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

function VerticalChevronLayer({
  width,
  height,
  bladeThickness,
  y,
}: {
  width: number;
  height: number;
  bladeThickness: number;
  y: number;
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
              Math.max(bladeThickness * 5, 0.018),
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
}: {
  width: number;
  height: number;
  bladeThickness: number;
  y: number;
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
              Math.max(bladeThickness * 5, 0.018),
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

  useFrame(({ clock }) => {
    const normalizedSpeed =
      Math.max(segment.engineeringSpeed, 0) *
      0.015;

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
                  : 0.016,
                8,
                8,
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
