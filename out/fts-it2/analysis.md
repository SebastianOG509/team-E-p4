# Analysis of FTS

## EQS3 (Scenario E-QS3 (disponibilidad del Traductor))

| Factor | Unavailability | Share |
|--------|----------------|-------|
| TRA, TRS (β = 0.1) | 0.0520 % | 100 % |

Chain availability: **99.948 %** (4.6 h/year); target 99.9: **met**

## FTSApply (Scenario SoS-QS1 (M4, aplicar resultados en el FTS))

| Stage | Budget |
|-------|--------|
| CON | 30000 ms |

Chain latency: **30000 ms**; target 30000: **met**

## SoSQS1M4 (Scenario SoS-QS1 (M4))

| Stage | Budget |
|-------|--------|
| RGW | 200000 ms |
| SoS_K5 | 40000 ms |
| NCG | 230000 ms |
| SoS_K32 | 10000 ms |
| CGW | 300000 ms |

Chain latency: **780000 ms**; target 900000: **met**
