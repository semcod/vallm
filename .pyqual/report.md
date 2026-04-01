# Pyqual Pipeline Report

**Generated:** 2026-04-01 15:46:22
**Pipeline run:** 2026-04-01T12:12:40.020421+00:00

---

## 🔄 Pipeline Flow Diagram

```mermaid
flowchart LR
    S0["analyze<br/>39.7s"]
    style S0 fill:#90EE90
    S1["validate<br/>0.9s"]
    style S1 fill:#90EE90
    S0 --> S1
    S2["lint<br/>0.0s"]
    style S2 fill:#90EE90
    S1 --> S2
    S3["test<br/>6.7s"]
    style S3 fill:#90EE90
    S2 --> S3
    S4["push<br/>1.9s"]
    style S4 fill:#90EE90
    S3 --> S4
    S5["publish<br/>3.1s"]
    style S5 fill:#90EE90
    S4 --> S5
    S6["markdown_report<br/>2.2s"]
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
│  ✓ lint                         0.0s 🟢        │
│  ✓ test                         6.7s 🟢        │
│  ✓ push                         1.9s 🟢        │
│  ✓ publish                      3.1s 🟢        │
│  ✓ markdown_report              2.2s 🟢        │
├─────────────────────────────────────────────────────────────────┤
│  🎉 ALL GATES PASSED ✓                                           │
│  ⏱️  Total time: 54.7s                                          │
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

#### ✅ lint
- **Status:** passed
- **Duration:** 0.0s
- **Return code:** 0

#### ✅ test
- **Status:** passed
- **Duration:** 6.7s
- **Return code:** 0

#### ✅ push
- **Status:** passed
- **Duration:** 1.9s
- **Return code:** 0

#### ✅ publish
- **Status:** passed
- **Duration:** 3.1s
- **Return code:** 0

#### ✅ markdown_report
- **Status:** passed
- **Duration:** 2.2s
- **Return code:** 0


---

## 📝 Summary

✅ **All quality gates passed!** Pipeline completed successfully in 54.7s.
