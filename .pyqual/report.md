# Pyqual Pipeline Report

**Generated:** 2026-04-01 14:04:30
**Pipeline run:** 2026-04-01T12:04:28.663223+00:00

---

## 🔄 Pipeline Flow Diagram

```mermaid
flowchart LR
    S0["claude_fix<br/>6.4s"]
    style S0 fill:#FFB6C1
    S1["prefact<br/>64.4s"]
    style S1 fill:#90EE90
    S0 --> S1
    S2["verify<br/>0.6s"]
    style S2 fill:#90EE90
    S1 --> S2
    S3["markdown_report<br/>2.4s"]
    style S3 fill:#90EE90
    S2 --> S3
    S4["unknown<br/>0.0s"]
    style S4 fill:#FFB6C1
    S3 --> S4
    S5["analyze<br/>36.8s"]
    style S5 fill:#90EE90
    S4 --> S5
    S6["validate<br/>1.3s"]
    style S6 fill:#90EE90
    S5 --> S6
    S7["lint<br/>0.0s"]
    style S7 fill:#90EE90
    S6 --> S7
    S8["test<br/>9.2s"]
    style S8 fill:#90EE90
    S7 --> S8
    S9["push<br/>5.6s"]
    style S9 fill:#90EE90
    S8 --> S9
    S10["publish<br/>2.9s"]
    style S10 fill:#90EE90
    S9 --> S10
    G["✗ Gates Failed"]
    style G fill:#FFB6C1,stroke:#DC143C,stroke-width:3px
    S10 --> G
```

## 📈 ASCII Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                    PYQUAL PIPELINE FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│  ✗ claude_fix                   6.4s 🔴        │
│  ✓ prefact                     64.4s 🟢        │
│  ✓ verify                       0.6s 🟢        │
│  ✓ markdown_report              2.4s 🟢        │
│  ✗ unknown                      0.0s 🔴        │
│  ✓ analyze                     36.8s 🟢        │
│  ✓ validate                     1.3s 🟢        │
│  ✓ lint                         0.0s 🟢        │
│  ✓ test                         9.2s 🟢        │
│  ✓ push                         5.6s 🟢        │
│  ✓ publish                      2.9s 🟢        │
├─────────────────────────────────────────────────────────────────┤
│  ❌ SOME GATES FAILED                                            │
│  ⏱️  Total time: 129.6s                                          │
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

#### ✅ prefact
- **Status:** passed
- **Duration:** 64.4s
- **Return code:** 0

#### ✅ verify
- **Status:** passed
- **Duration:** 0.6s
- **Return code:** 0

#### ✅ markdown_report
- **Status:** passed
- **Duration:** 2.4s
- **Return code:** 0

#### ❌ unknown
- **Status:** failed
- **Duration:** 0.0s

#### ✅ analyze
- **Status:** passed
- **Duration:** 36.8s
- **Return code:** 0

#### ✅ validate
- **Status:** passed
- **Duration:** 1.3s
- **Return code:** 0

#### ✅ lint
- **Status:** passed
- **Duration:** 0.0s
- **Return code:** 0

#### ✅ test
- **Status:** passed
- **Duration:** 9.2s
- **Return code:** 0

#### ✅ push
- **Status:** passed
- **Duration:** 5.6s
- **Return code:** 0

#### ✅ publish
- **Status:** passed
- **Duration:** 2.9s
- **Return code:** 0


---

## 📝 Summary

❌ **Some quality gates failed.** Review the stage details above.
