# Pyqual Pipeline Report

**Generated:** 2026-04-01 13:57:36
**Pipeline run:** 2026-04-01T11:57:34.834434+00:00

---

## 🔄 Pipeline Flow Diagram

```mermaid
flowchart LR
    S0["claude_fix<br/>6.4s"]
    style S0 fill:#FFB6C1
    S1["markdown_report<br/>2.4s"]
    style S1 fill:#90EE90
    S0 --> S1
    S2["analyze<br/>58.0s"]
    style S2 fill:#90EE90
    S1 --> S2
    S3["validate<br/>1.1s"]
    style S3 fill:#90EE90
    S2 --> S3
    S4["lint<br/>0.0s"]
    style S4 fill:#90EE90
    S3 --> S4
    S5["test<br/>7.7s"]
    style S5 fill:#90EE90
    S4 --> S5
    S6["prefact<br/>64.4s"]
    style S6 fill:#90EE90
    S5 --> S6
    S7["unknown<br/>0.0s"]
    style S7 fill:#FFB6C1
    S6 --> S7
    S8["verify<br/>0.6s"]
    style S8 fill:#90EE90
    S7 --> S8
    G["✗ Gates Failed"]
    style G fill:#FFB6C1,stroke:#DC143C,stroke-width:3px
    S8 --> G
```

## 📈 ASCII Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                    PYQUAL PIPELINE FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│  ✗ claude_fix                   6.4s 🔴        │
│  ✓ markdown_report              2.4s 🟢        │
│  ✓ analyze                     58.0s 🟢        │
│  ✓ validate                     1.1s 🟢        │
│  ✓ lint                         0.0s 🟢        │
│  ✓ test                         7.7s 🟢        │
│  ✓ prefact                     64.4s 🟢        │
│  ✗ unknown                      0.0s 🔴        │
│  ✓ verify                       0.6s 🟢        │
├─────────────────────────────────────────────────────────────────┤
│  ❌ SOME GATES FAILED                                            │
│  ⏱️  Total time: 140.6s                                          │
└─────────────────────────────────────────────────────────────────┘
```

### 📊 Quality Gates

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|

### 🔧 Stage Execution Details

#### ❌ claude_fix
- **Status:** failed
- **Duration:** 6.4s
- **Return code:** 1

#### ✅ markdown_report
- **Status:** passed
- **Duration:** 2.4s
- **Return code:** 0

#### ✅ analyze
- **Status:** passed
- **Duration:** 58.0s
- **Return code:** 0

#### ✅ validate
- **Status:** passed
- **Duration:** 1.1s
- **Return code:** 0

#### ✅ lint
- **Status:** passed
- **Duration:** 0.0s
- **Return code:** 0

#### ✅ test
- **Status:** passed
- **Duration:** 7.7s
- **Return code:** 0

#### ✅ prefact
- **Status:** passed
- **Duration:** 64.4s
- **Return code:** 0

#### ❌ unknown
- **Status:** failed
- **Duration:** 0.0s

#### ✅ verify
- **Status:** passed
- **Duration:** 0.6s
- **Return code:** 0


---

## 📝 Summary

❌ **Some quality gates failed.** Review the stage details above.
