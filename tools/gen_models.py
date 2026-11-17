"""Writes the four models of the Fluvial Transportation System (FTS), one per iteration of
Delivery 4, from the tables of Delivery 2 (tools/fts_data.json) and from models/sos.arch.

  python3 tools/gen_models.py  ->  models/fts-it1.arch  starting structure (Delivery 1)
                                   models/fts-it2.arch  resulting structure (Delivery 2)
                                   models/fts-it3.arch  same structure + what scenario B needs
                                   models/fts-it4.arch  redesigned structure
                                   invalid/correspondence.arch  (it1 with a diverging SoS_K19a)
The boundary components and the global connectors are copied verbatim from sos.arch.
"""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
data = json.load(open(os.path.join(ROOT, 'tools', 'fts_data.json'), encoding='utf-8'))
sos = open(os.path.join(ROOT, 'models', 'sos.arch'), encoding='utf-8').read().split('\n')

# ── pieces copied from sos.arch ──────────────────────────────────────────────
constituents = [l for l in sos if l.startswith('constituent ')]
boundary = {re.match(r'component (\w+)', l).group(1): l for l in sos
            if l.startswith('component ') and ' tier T2 ' in l}
blocks, cur = {}, None
for l in sos:
    m = re.match(r'connector (\w+)', l)
    if m:
        cur = m.group(1); blocks[cur] = [l]
    elif cur and l.startswith('  '):
        blocks[cur].append(l)
    else:
        cur = None

FTS_GLOBAL = ['SoS_K4a', 'SoS_K4b', 'SoS_K10a', 'SoS_K10b', 'SoS_K15', 'SoS_K16',
              'SoS_K19a', 'SoS_K19b', 'SoS_K28a', 'SoS_K28b', 'SoS_K31a', 'SoS_K31b', 'SoS_K35']
M4_ONLY = ['SoS_K5', 'SoS_K32']          # to compose the budgets of SoS-QS1 (M4) as in sos.arch

# ── feedback on Delivery 3, point 3: events that reached a T3 service without the broker ──
# Both are point-to-point submissions from a T1 client to the one service that records them;
# the event is born when that service publishes to the broker (E-K21, E-K25).
RECLASSIFIED = {'E-K19': 'data_flow',    # dock terminal -> Custody: handover record to register
                'E-K38': 'data_flow'}    # captain's app -> Tracking: report to register

# ── properties of the components (ms; availability in %; capacity in jobs/s) ──
# Primitive parameters only (Delivery 2): A1 capacity of the Translator, A2 durable write,
# A3 health probe, H2/H3 buffer and forwarding rate, heartbeat of E-QS6. No queueing time.
IT2 = {'TRA': 'availability 99.5 capacity 100 discipline priority',
       'TRS': 'availability 99.5',
       'BRO': 'store role broker', 'CON': 'latency 30000',
       'UAB': 'period 10000 misses 3',
       'BUF': 'capacity 50 store buffer 1280 period 10000'}
IT3 = dict(IT2, TRA='availability 99.5 capacity 100 discipline priority period 2000 misses 3',
           TRS='availability 99.5 capacity 100 discipline priority standby TRA switch 2000',
           FGW='store')
IT4 = dict(IT3, UAB='period 8000 misses 3', BUF='capacity 50 store buffer 1280 period 8000',
           TUR='store', PRO='store', CON='latency 30000 store')
COMP = {'it1': {'TRA': 'availability 99.5 capacity 100', 'BRO': 'role broker', 'CON': 'latency 30000'},
        'it2': IT2, 'it3': IT3, 'it4': IT4}
# Latency (ms) of a hop: processing budget of the stage, never a waiting time in a queue.
E1_LAT = {'E-K19': 10, 'E-K21': 10, 'E-K27': 10}              # 10 ms per stage (as A1)
E2_LAT = {'E-K19': 30, 'E-K21': 30, 'E-K27': 30,              # + 20 ms durable write (A2)
          'E-K55': 20,                                        # durable write in the queue (A2)
          'E-K59': 2000,                                      # persist + durable ack (E-QS2)
          'E-K29': 5000}                                      # propagation budget of the notice
                                                              # SEG -> Panel (E-QS6), on its last hop
CONN = {'it1': E1_LAT, 'it2': E2_LAT, 'it3': E2_LAT, 'it4': E2_LAT}
TITLE = {'it1': 'iteration 1, starting structure (Delivery 1 with the parameters of Delivery 2)',
         'it2': 'iteration 2, resulting structure of Delivery 2',
         'it3': 'iteration 3, resulting structure of Delivery 2 + what scenario B (E-QS3) needs',
         'it4': 'iteration 4, redesigned structure'}

# ── quality scenarios (Delivery 2, section 5) with their six parts ───────────
QUALITIES = '''// Quality scenarios (Delivery 2, section 5); the artifact refers to elements of the model
quality EQS1 "Custodia oportuna durante la reconciliación"
  attribute "Rendimiento"
  source "Terminal de Operación de Muelle y Coordinación Nacional (aviso de restablecimiento)"
  stimulus "Tras 4 h sin rastreo carretero llega «restablecido» por SoS-K35 mientras el muelle registra traspasos a 10 eventos/s"
  artifact E_K19, E_K20, E_K21, E_K26, E_K27, CUS, BRO, TRA, FGW, E_K31, E_K32, E_K33, E_K34, CON
  environment "Pico H1; 40 unidades pendientes (H4); la frontera NCS responde en <= 2 s; se mantiene el reenvío H3"
  response "Persistir cada traspaso y entregar su evento canónico al Fluvial Gateway sin esperar la reconciliación; reconciliar las 40 unidades"
  measure "Custodia p95 <= 30 s de E-K19 a E-K27; 0 eventos aceptados perdidos; reconciliación <= 300 s, <= 2 intentos/s y <= 80 intentos"
quality EQS2 "Preservación de posiciones sin cobertura"
  attribute "Confiabilidad (resiliencia y recuperabilidad)"
  source "Interrupción del enlace de comunicaciones del convoy"
  stimulus "Se pierde E-K22 durante 1.800 s; la Unidad a Bordo sigue produciendo una posición cada 10 s; luego se recupera el enlace"
  artifact UAB, E_K22, IOT, E_K23, SEG, E_K24, ALT, E_K25, E_K28
  environment "Partición de hasta 5 de los 50 convoyes con carga H1; al reconectar opera la carga H3"
  response "Guardar cada posición antes de enviarla, conservarla durante la partición y enviarla al reconectar, sin duplicados"
  measure "0 posiciones perdidas de 900; reserva >= 256 KiB por convoy; rezago persistido <= 60 s tras reconectar; posiciones nuevas p95 <= 15 s"
quality EQS3 "Continuidad ante la caída del Traductor"
  attribute "Disponibilidad"
  source "Falla de ejecución de una instancia del Traductor de Modelo Canónico"
  stimulus "La instancia deja de procesar mensajes durante asignaciones de turnos SoS-K4 y coordinación de retiros SoS-K28"
  artifact TRA, E_K1, E_K2, E_K6, E_K7, E_K39, E_K40, E_K41, E_K42, SoS_K4a, SoS_K4b, SoS_K28a, SoS_K28b
  environment "Pico H1, carga de reenvío H3 y una instancia caída; Gateway, bases y servicios permanecen disponibles"
  response "Detectar la falla y continuar las transformaciones; preservar solicitudes aceptadas y evitar turnos o retiros duplicados"
  measure "Traducción restablecida <= 10 s; en 60 min >= 99,9 % de las operaciones de cada ruta <= 15 s y p95 <= 5 s; 0 operaciones aceptadas perdidas"
quality EQS4 "Rechazo de retiros y custodias falsificados"
  attribute "Seguridad"
  source "Actor externo que suplanta a Carretera o altera un registro de custodia"
  stimulus "Inyecta una confirmación SoS-K28b falsa o una custodia sin origen autorizado"
  artifact FGW, TUR, CUS, E_K19, E_K41, E_K42, SoS_K28b, SoS_K15
  environment "Ataque H5 de 100 mensajes/s durante 15 min sobre el pico H1"
  response "Verificar origen, autorización, integridad, vigencia y correlación; rechazar y registrar evidencia"
  measure "0 falsificaciones aceptadas; rechazo p95 <= 2 s; registro <= 5 s; alerta <= 30 s"
quality EQS5 "Cambio obligatorio de CargoUnit contenido en el Traductor"
  attribute "Evolutividad"
  source "Proceso conjunto de evolución del contrato canónico"
  stimulus "Se agrega un atributo obligatorio a CargoUnit, derivable de datos internos"
  artifact TRA, FGW, E_K27, E_K40, E_K44
  environment "Versiones anterior y nueva coexisten 24 h bajo carga H1"
  response "Incorporar validación y mapeo en el Traductor y conservar los contratos internos"
  measure "<= 16 horas-persona; 1 componente modificado; 0 cambios en servicios, bases y contratos internos"
quality EQS6 "Detección del silencio y vigencia de la telemetría"
  attribute "Confiabilidad (tolerancia a fallos)"
  source "Unidad a Bordo, enlace de campo o elemento interno que deja de emitir telemetría"
  stimulus "Se interrumpe el flujo que alimenta a SoS-K16"
  artifact UAB, E_K22, IOT, E_K23, SEG, E_K25, BRO, E_K29, PAN
  environment "Pico H1 y recuperación H3; pérdida de E-K22"
  response "Emitir latidos cada 10 s y marcar la telemetría como no vigente al faltar señales"
  measure "Estado no vigente visible localmente <= 35 s desde el último latido válido (3 latidos ausentes + propagación <= 5 s)"
quality SoSQS1 "SoS-QS1: operación degradada sin rastreo carretero (contribución del FTS a M4)"
  attribute "Resiliencia"
  source "Proveedor de nube que aloja el rastreo de Carretera"
  stimulus "Cae SoS-K6 durante 4 h; al volver, Coordinación Nacional avisa «restablecido» por SoS-K35"
  artifact FGW, NCG, SoS_K19a, SoS_K19b, SoS_K35, CON
  environment "40 unidades pendientes; <= 2 intentos/s por SoS-K19a (P7); máximo 1 reintento; respuesta de frontera <= 2 s"
  response "Consultar el estado consolidado de las unidades pendientes y sustituir las estimaciones por datos reales"
  measure "M4: reconciliación local del FTS <= 300 s (270 s para consultas y reintentos, 30 s para aplicar resultados)"
'''
TACTICS = '''// Tactics and patterns (Delivery 2, sections 6.2 and 7): scenario, elements introduced and changed
tactic PersistentPriorityQueue "Búfer persistente y priorización de colas" for EQS1
  introduces COL, E_K55, E_K56 changes BRO, TRA, E_K26
tactic StoreAndForward "Almacenar y reenviar a bordo, con acuse duradero" for EQS2
  introduces BUF, E_K57, E_K58, E_K59, E_K60 changes UAB, SEG, E_K22, E_K23, E_K24
tactic PrimaryStandby "Redundancia primary-standby con sondeo de salud y conmutación" for EQS3
  introduces TRS, E_K61, E_K62, E_K63, E_K64, E_K65 changes TRA, FGW
tactic PolicyEnforcement "Punto de control de políticas, verificador de correlación y auditoría" for EQS4
  introduces AUD, E_K66, E_K67, E_K68, E_K69 changes FGW, CUS, TUR, E_K19
tactic AntiCorruptionLayer "Capa anticorrupción versionada" for EQS5
  changes TRA
tactic HeartbeatFreshness "Latido cada 10 s y filtro de vigencia" for EQS6
  changes UAB, SEG, E_K22, E_K23, E_K25, E_K29, PAN
tactic DegradedMode "Aviso de estado de servicio, límite P7 y reconciliación" for SoSQS1
  introduces E_K47, E_K48, E_K49, E_K50, E_K51, E_K52, E_K53, E_K54 changes CON, TUR, PRO, BRO
'''
TACTICS_IT4 = '''// Tactics introduced or adjusted in iteration 4 (from the results of iterations 2 and 3)
tactic CallerRetention "Retención y reintento idempotente en el emisor mientras el Traductor conmuta" for EQS3
  changes TUR, PRO, CON
tactic FasterHeartbeat "Latido cada 8 s (ajuste del periodo)" for EQS6
  changes UAB, BUF, E_K22
'''

# ── scenarios for simulation: stimulus (workloads), environment (faults, delays), measures ──
VIA_BROKER = {False: ('BRO', 'E_K26'), True: ('BRO -> COL -> BRO', 'E_K55, E_K56, E_K26')}


def load(e2, at, p=''):
    """Load of the Translator in the recovery (Delivery 2, section 8): custody 10, positions 5,
    backlog 50 (900 positions, H3), SoS-K4 2 x 10, SoS-K28 2 x 5 and SoS-K31 2 x 5 operations/s.
    Workload names are unique in a model, so those of scenario B carry the prefix p."""
    bro, k = VIA_BROKER[e2]
    return f'''  workload {p}Custody rate 10 priority 1 : TMU -> CUS -> {bro} -> TRA -> FGW
    via E_K19, E_K21, {k}, E_K27
  workload {p}Positions rate 5 priority 2 : UAB -> IOT -> SEG -> {bro} -> TRA -> FGW
    via E_K22, E_K23, E_K25, {k}, E_K28
  workload {p}Backlog rate 50 count 900 at {at} priority 3 : IOT -> SEG -> {bro} -> TRA -> FGW
    via E_K23, E_K25, {k}, E_K28
  workload {p}K4 rate 10 priority 2 : FGW -> TRA -> TUR -> BOF -> TUR -> TRA -> FGW
    via E_K1, E_K2, E_K3, E_K4, E_K6, E_K7
  workload {p}K28 rate 5 priority 2 : TUR -> TRA -> FGW -> RGW -> FGW -> TRA -> TUR
    via E_K39, E_K40, SoS_K28a, SoS_K28b, E_K41, E_K42
  workload {p}K31 rate 5 priority 2 : CGW -> FGW -> TRA -> PRO -> TRA -> FGW -> CGW
    via SoS_K31a, E_K43, E_K44, E_K45, E_K46, SoS_K31b
'''


def recovery(e2):
    return f'''// Scenario A (E-QS1 and SoS-QS1 M4): recovery load on the shared Translator. The 90 s after
// the warm-up are the reconciliation window; nothing is measured before «restablecido» (t = 60 s).
scenario Recovery "E-QS1"
{load(e2, 60)}  workload Reconcile rate 2 count 40 at 60 retry 1 priority 3 : CON -> TRA -> FGW -> NCG -> FGW -> TRA -> CON
    via E_K31, E_K32, SoS_K19a, SoS_K19b, E_K33, E_K34
  delay NcsResponse at NCG for 2000
  vary TRA : 50, 60, 70, 80, 90, 120
  vary NcsResponse : 1000, 5000, 30000
  vary Reconcile.retry : 0, 0.5
  vary Reconcile : 0.25, 0.5, 1
  measure p95_latency Custody <= 30 s of EQS1 as "P1a custodia p95"
  measure p95_latency Positions <= 15 s of EQS2 as "P2c posiciones nuevas p95"
  measure p95_latency K4 <= 5 s of EQS3 as "P3f turno K4 p95 (sin falla)"
  measure completion Reconcile <= 270 s of SoSQS1 as "P5 reconciliación (consultas)"
  run 150 warmup 60 replications 10
'''


def partition(e2):
    if not e2:
        return '''// Scenario E-QS2 / E-QS6: partition of the river-land link E-K22 for 1 800 s (5 convoys, H2)
scenario Partition "E-QS2 / E-QS6"
  workload Affected rate 0.5 : UAB -> IOT -> SEG -> ALT
    via E_K22, E_K23, E_K24
  fault E_K22 down at 100 for 1800
  measure lost Affected <= 0 events of EQS2 as "P2a posiciones perdidas"
  measure drain Affected <= 60 s of EQS2 as "P2b persistencia del rezago"
  measure detection <= 35 s of EQS6 as "P4 detección del silencio"
  run 2100 warmup 0 replications 10
'''
    return '''// Scenario E-QS2 / E-QS6: partition of the river-land link for 1 800 s (5 convoys, H2). The link
// carries E-K22 (positions and heartbeats) and E-K58 (backlog of the buffer): both are down.
scenario Partition "E-QS2 / E-QS6"
  workload Affected rate 0.5 : UAB -> BUF -> IOT -> SEG -> IOT
    via E_K57, E_K58, E_K23, E_K59
  workload Stale on UAB : SEG -> BRO -> PAN
    via E_K25, E_K29
  fault E_K22 down at 100 for 1800
  fault E_K58 down at 100 for 1800
  vary BUF.buffer : 600, 900
  vary UAB.period : 6000, 8000, 9000, 12000
  measure lost Affected <= 0 events of EQS2 as "P2a posiciones perdidas"
  measure drain Affected <= 60 s of EQS2 as "P2b persistencia del rezago"
  measure detection <= 35 s of EQS6 as "P4 detección del silencio"
  run 2100 warmup 0 replications 10
'''


def failover():
    return f'''// Scenario B (E-QS3): one instance of the Translator fails for 300 s (manual recovery when
// there is no standby) under peak H1 and the H3 backlog, in a 60 min window.
scenario Failover "E-QS3"
{load(True, 600, 'F')}  fault TRA down at 600 for 300
  measure restore <= 10 s of EQS3 as "P3a traducción restablecida"
  measure p999_latency FK4 <= 15 s of EQS3 as "P3b turno K4 99,9 %"
  measure p999_latency FK28 <= 15 s of EQS3 as "P3c retiro K28 99,9 %"
  measure lost FK4 <= 0 events of EQS3 as "P3d turnos K4 perdidos"
  measure lost FK28 <= 0 events of EQS3 as "P3e retiros K28 perdidos"
  measure lost FCustody <= 0 events of EQS1 as "P1b custodia perdida"
  run 3600 warmup 0 replications 10
'''


ANALYSES = {
    False: '''// E-QS3: availability of the translation (Delivery 2, 8.1.3); chain of property S1
analysis EQS3 scenario "E-QS3 (disponibilidad del Traductor)" availability target 99.9 :
  TRA
''',
    True: '''// E-QS3: availability with a standby replica and common cause (Delivery 2, 8.1.3); chain of S1
analysis EQS3 scenario "E-QS3 (disponibilidad del Traductor)" availability target 99.9 :
  [TRA | TRS] beta 0.10
'''}
ANALYSES_COMMON = '''// SoS-QS1 (M4): sub-budget of the FTS to apply the results of the reconciliation (Delivery 2, 5.2)
analysis FTSApply scenario "SoS-QS1 (M4, aplicar resultados en el FTS)" latency target 30000 :
  CON
// SoS-QS1 (M4): composition of the joint budgets, as in sos.arch
analysis SoSQS1M4 scenario "SoS-QS1 (M4)" latency target 900000 :
  RGW, SoS_K5, NCG, SoS_K32, CGW
'''


def comp_line(c, extra):
    return f'component {c["id"]} "{c["label"]}" in FTS tier {c["tier"]} kind {c["kind"]}' + \
           (f' {extra}' if extra else '')


def conn_block(k, e2, latency):
    info = k['info_e2'] if e2 and k.get('info_e2') else k['info']
    nature = RECLASSIFIED.get(k['id'], k['nature'])
    lines = [f'connector {k["id"].replace("-", "_")} nature {nature} coupling {k["coupling"]}',
             f'  carries "{info}"']
    if k['id'] in latency:
        lines.append(f'  latency {latency[k["id"]]}')
    lines.append(f'  : {k["src"]} -> {k["dst"]}')
    return lines


def text(it):
    e2 = it != 'it1'
    out = [f'// Model (M1) of the Fluvial Transportation System (FTS): {TITLE[it]}',
           '// Generated by tools/gen_models.py from the tables of Delivery 2 and from sos.arch.',
           '// Language: core v2.0 (Laboratories 4 and 5) with the [E] extensions of team E.',
           'system FTS', ''] + constituents + ['']
    props = COMP[it]
    out.append('// Components of the FTS, by tier')
    for tier in ('T1', 'T2', 'T3', 'T4', 'T5'):
        out.append(f'// {tier}')
        if tier == 'T2':        # own boundary component: as in sos.arch, plus simulation properties
            out.append(boundary['FGW'] + (f' {props["FGW"]}' if 'FGW' in props else ''))
        for c in data['components']:
            if c['tier'] == tier and c['id'] != 'FGW' and (e2 or not c['e2_only']):
                out.append(comp_line(c, props.get(c['id'])))
    out += ['// T2 — boundary components of the other constituents (as in sos.arch)']
    out += [boundary[b] for b in ('CGW', 'PGW', 'RGW', 'LGW', 'NCG')]
    out += ['', '// Global connectors of the FTS (as in sos.arch)']
    for name in FTS_GLOBAL:
        out += blocks[name]
    out += ['// Global connectors outside the FTS, only to compose the budgets of SoS-QS1 (M4) as in sos.arch']
    for name in M4_ONLY:
        out += blocks[name]
    out += ['', '// Internal connectors of the FTS']
    for k in data['connectors']:
        if e2 or not k['e2_only']:
            out += conn_block(k, e2, CONN[it])
    out += ['', '// Analyses'] + (ANALYSES[e2] + ANALYSES_COMMON).rstrip('\n').split('\n')
    out += [''] + QUALITIES.rstrip('\n').split('\n')
    if e2:
        out += [''] + TACTICS.rstrip('\n').split('\n')
    if it == 'it4':
        out += TACTICS_IT4.rstrip('\n').split('\n')
    scenarios = recovery(e2) + partition(e2) + (failover() if it in ('it3', 'it4') else '')
    if it == 'it4':             # the redesign shortens the heartbeat: its sweep moves accordingly
        scenarios = scenarios.replace('vary UAB.period : 6000, 8000, 9000, 12000',
                                      'vary UAB.period : 6000, 9000, 10000, 12000')
    out += [''] + scenarios.rstrip('\n').split('\n')
    return '\n'.join(out) + '\n'


if __name__ == '__main__':
    for it in ('it1', 'it2', 'it3', 'it4'):
        path = os.path.join(ROOT, 'models', f'fts-{it}.arch')
        model = text(it)
        open(path, 'w', encoding='utf-8').write(model)
        print(path, '->', model.count('\ncomponent '), 'components,',
              model.count('\nconnector '), 'connectors')
    # Ill-formed with respect to sos.arch: the agreement of a global connector diverges.
    bad = text('it1').replace('agreement "Contrato de estado consolidado; regla de acceso y tasa P7"\n  : FGW -> NCG',
                              'agreement "Contrato de estado consolidado (sin tasa)"\n  : FGW -> NCG')
    bad = '// Diverges from sos.arch: the agreement of SoS_K19a was changed (correspondence check).\n' + bad
    open(os.path.join(ROOT, 'invalid', 'correspondence.arch'), 'w', encoding='utf-8').write(bad)
