# ADD Simulation Workspace V0.1

## Purpose

The Airflow Simulation Workspace is the first functional UI for configuring and
running Experimental Airflow Solver V0.1. It is an engineering input and result
inspection surface, not a CFD viewer. Editing does not run simulations; the user
must press **Run simulation**.

## Layout

The desktop-first page has three regions:

1. **Inputs** — inlet, grille/plenum, outlet grid, free area, deflectors,
   validation, reset, and run controls.
2. **Engineering 3D visualization** — a true Three.js scene containing the
   inlet, transparent plenum envelope, grille/outlet array, and every deflector
   in solver coordinates. Orbit controls provide rotate, pan, and zoom, with
   isometric, front, side, and top camera presets.
3. **Results** — status, conservation summary, heat-map selector, outlet matrix,
   selected-outlet detail, provenance, and experimental-model notice.

At laptop widths the three regions remain in columns. The long input panel
scrolls independently. Essential values are visible text, never hover-only.

## Inputs and units

| UI input | Unit | API field | Rule |
|---|---|---|---|
| SF-501 / SF-502 enabled state | boolean | `fans[].enabled` | At least one fan above 0 Hz |
| SF-501 / SF-502 frequency | Hz | `fans[].frequency_hz` | 0 through verified 60 Hz maximum |
| Grille width/height | mm | `grille_width_mm`, `grille_height_mm` | Greater than zero |
| Plenum depth | mm | `plenum_depth_mm` | Greater than zero |
| Inlet width/height | mm | `inlet_width_mm`, `inlet_height_mm` | Greater than zero |
| Inlet position X/Y/Z | m | `inlet.position` | Explicit finite solver coordinates |
| Inlet direction X/Y/Z | unit vector | `inlet.direction` | Finite and non-zero; normalized before solver use |
| Rows/columns | count | `rows`, `columns` | Positive integers; V0.1 requires eight cells |
| Outlet width/height | mm | `outlet_width_mm`, `outlet_height_mm` | Greater than zero |
| Free area | % | `free_area_ratio` | Blank or greater than 0% through 100% |
| Deflector width/height | m | `width_m`, `height_m` | Greater than zero |
| Deflector X/Y/Z | m | `position_m` | Existing solver coordinates |
| Deflector angle | degrees | `angle_deg_about_y` | About global +Y |

Entered free area is normalized only for transport: 70% becomes the explicit
ratio `0.70`. The UI-only `free_area_percent` field is removed before request
serialization and is never accepted by the strict API schema. Blank remains
JSON `null`; the UI never substitutes 100%. The
temporary backward-compatible inlet default is position `(0, 0, depth)` and
direction `(0, 0, -1)`, but both are visible and editable. Six axial presets and
a custom vector are provided. The custom vector is normalized at the frontend
request boundary and again defensively by the API adapter. A zero-length vector
is rejected before solver execution. Zero deflectors is a valid baseline.

## Solver request flow

1. Page-local state is validated.
2. The typed client creates `WorkspaceSimulationRequest`.
3. `POST /api/v1/simulations/airflow` evaluates the two governed fan profiles,
   sums their CFM, and maps that total plus explicit geometry into the existing
   immutable `ExperimentalAirflowInput`. Frequency never enters the solver.
4. The API calls `ExperimentalAirflowSolver.solve()`; TypeScript contains no
   airflow allocation model.
5. The API packages solver values, availability, units, reasons, and provenance.
6. The UI formats and renders the response without calculating engineering data.

The run button is disabled during a request. HTTP and solver errors appear in a
visible, localized alert. Raw Pydantic/backend details are secondary and are
available only in an expandable technical diagnostic. Reset restores the demonstration configuration and clears the
last result; it does not change any golden fixture.

## Verified site fan model

`SF-501` and `SF-502` are governed equipment identifiers, not generic display
names. Both profiles use the verified nameplate values: 100 HP, 110000 m³/h,
1600 Pa, and 60 Hz maximum. The FastAPI fan adapter treats 60 Hz as rated and
applies only the approved affinity relationships:

- current airflow = 110000 × Hz / 60;
- current static pressure = 1600 × (Hz / 60)²;
- total solver airflow = SF-501 airflow + SF-502 airflow, converted to CFM.

All calculated fan values carry the label **Estimated using Fan Affinity Laws**
and calculation provenance. They are never described as measurements. Disabled
fans contribute available zero; if both fans provide zero flow, the request is
rejected before solver execution. The shared inlet bulk velocity is calculated
by the backend from each fan's airflow component and the explicitly supplied
inlet area. No fan curve, duct loss, power, or energy calculation is inferred.

Experimental Solver V0.1 has one inlet boundary. Consequently both real fans
feed the same configured inlet position and direction in this version. Separate
fan duct branches or independently located solver inlets require the reviewed
future multiple-inlet interface and cannot be represented honestly by the
current solver.

## Localization

The complete workspace supports Traditional Chinese (`zh-TW`) and English
(`en`). Traditional Chinese is the default. The selected language is stored in
local storage under `add.language` and restored on the next visit. Navigation,
titles, controls, validation, user-facing API errors, empty/results states,
heat-map controls, outlet details, provenance labels, unavailable-velocity
reasons, and the experimental-model notice use the same governed dictionary.

## Result fields

The summary shows inlet CFM/CMH, summed outlet CFM/CMH, conservation error and
status, backend-packaged uniformity (`minimum / maximum`), outlet count, and
deflector count. Every outlet exposes:

- airflow percentage, CFM, and m³/h;
- bulk outlet velocity in m/s when available;
- geometric area, free-area ratio, and effective area;
- calculation provenance and any unavailable reason code.

The UI formats decimal places only. It does not independently calculate
conversion, area, velocity, conservation, or uniformity.

## Unavailable values

Unavailable velocity renders as **Velocity unavailable**, not zero or an
unexplained placeholder. The selected-outlet panel shows the backend reason
code. Missing free area preserves percentage, CFM, and CMH while velocity stays
unavailable.

## Engineering 3D visualization and heat-map meaning

The 3D layer is presentation-only. Geometry editing rebuilds its immutable scene
projection immediately but does not call the API. The solver is still called
only by **Run simulation**. Canonical solver coordinates use X for left/right,
Y across the outlet plane, and Z for vertical/plenum depth; the grille/outlet
plane is Z=0. Three.js uses Y as visual up, so the presentation adapter maps
solver `(X,Y,Z)` to scene `(X,Z,Y)` without reordering API or solver values.

Every deflector is rendered as a thin physical plate at its submitted X/Y/Z
position, with width, height, and rotation about global +Y taken directly from
the existing request model. Zero, one, and multiple deflectors are supported.
Engineering annotations can be hidden without changing geometry.

Before a completed run, outlets use a neutral geometry material and particle
indicators are unavailable. After a completed run, the selectable heat metrics
are Airflow %, CFM, m³/h, and m/s. Each outlet material uses only its
corresponding solver value. The min/max normalization used to select a display
colour is a presentation transform and is not exported as an engineering
quantity.

Particles are engineering indicators, not streamlines. They exist only after
solver output is available. SF-501 and SF-502 have independent emitter groups;
a disabled fan creates no emitter particles. Emitter origin and direction use
the shared canonical inlet, density is proportional to the backend fan airflow,
and animation rate is proportional to backend inlet bulk velocity. Outlet
indicator density and rate use solver outlet airflow and velocity respectively.

The current solver exports no spatial trajectories or per-fan outlet
attribution. EVE therefore does not connect inlet emitters to outlets with an
invented curve. Short inlet-direction indicators and short outlet-normal
indicators remain deliberately disconnected. A continuous redirected particle
path cannot be claimed until a reviewed solver output provides that path.
Editing geometry, fan state/frequency, or inlet state hides all prior results,
heat maps, and particles as stale.

## Experimental-model disclaimer

The result panel identifies **Experimental Airflow Solver V0.1** and states:

> This is an experimental distribution model, not CFD. It does not model
> pressure, turbulence, resistance, or full fluid dynamics.

## Current limitations

- V0.1 accepts exactly eight outlets; other positive grid sizes are rejected.
- The default inlet remains top-centre with `-Z` direction for compatibility,
  but position and direction are configurable.
- Outlet centers are uniformly generated from rows and columns; per-cell editing
  and drag-and-drop are out of scope.
- The 3D scene communicates governed input geometry and solver allocation; it
  does not display a computed continuous flow field.
- A direction pointing away from every outlet may be rejected by Experimental
  Airflow Solver V0.1 because it has no usable positive distribution weights.
  The UI does not fabricate an allocation. For example, the default top inlet
  cannot produce an upward-to-outlet allocation without changing the layout.
- Per-outlet positions are still generated by the existing V0.1 adapter.
- No persistence, login, cloud storage, optimization, or recommendations.
- Provenance is shown as raw governed backend data; a friendlier narrative can
  be added later without changing its source contract.
