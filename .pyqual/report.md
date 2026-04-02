# Pyqual Pipeline Report

**Generated:** 2026-04-01 15:57:06
**Pipeline run:** 2026-04-01T13:57:04.323076+00:00

---

## 🔄 Pipeline Flow Diagram

```mermaid
flowchart LR
    S0["analyze<br/>39.7s"]
    style S0 fill:#90EE90
    S1["validate<br/>0.9s"]
    style S1 fill:#90EE90
    S0 --> S1
    S2["markdown_report<br/>2.9s"]
    style S2 fill:#90EE90
    S1 --> S2
    S3["lint<br/>0.1s"]
    style S3 fill:#90EE90
    S2 --> S3
    S4["test<br/>8.0s"]
    style S4 fill:#90EE90
    S3 --> S4
    S5["push<br/>2.3s"]
    style S5 fill:#90EE90
    S4 --> S5
    S6["publish<br/>4.0s"]
    style S6 fill:#90EE90
    S5 --> S6
    G["✓ All Gates Passed"]
    style G fill:#90EE90,stroke:#228B22,stroke-width:3px
    S6 --> G
```

## 📈 ASCII Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                    PYQUAL PIPELINE FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│  ✓ analyze                     39.7s 🟢        │
│  ✓ validate                     0.9s 🟢        │
│  ✓ markdown_report              2.9s 🟢        │
│  ✓ lint                         0.1s 🟢        │
│  ✓ test                         8.0s 🟢        │
│  ✓ push                         2.3s 🟢        │
│  ✓ publish                      4.0s 🟢        │
├─────────────────────────────────────────────────────────────────┤
│  🎉 ALL GATES PASSED ✓                                           │
│  ⏱️  Total time: 57.8s                                          │
└─────────────────────────────────────────────────────────────────┘
```

### 📊 Quality Gates

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| coverage | 63.9% | >= 55.0% | ✅ PASS |

### 🔧 Stage Execution Details

#### ✅ analyze
- **Status:** passed
- **Duration:** 39.7s
- **Return code:** 0

#### ✅ validate
- **Status:** passed
- **Duration:** 0.9s
- **Return code:** 0

#### ✅ markdown_report
- **Status:** passed
- **Duration:** 2.9s
- **Return code:** 0

#### ✅ lint
- **Status:** passed
- **Duration:** 0.1s
- **Return code:** 0

#### ✅ test
- **Status:** passed
- **Duration:** 8.0s
- **Return code:** 0

#### ✅ push
- **Status:** passed
- **Duration:** 2.3s
- **Return code:** 0

#### ✅ publish
- **Status:** passed
- **Duration:** 4.0s
- **Return code:** 0


---

## 📝 Summary

✅ **All quality gates passed!** Pipeline completed successfully in 57.8s.
