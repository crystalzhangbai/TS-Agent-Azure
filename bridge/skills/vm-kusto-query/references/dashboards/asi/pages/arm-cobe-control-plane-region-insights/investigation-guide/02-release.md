# Release

> Source: **ARM CoBe Control Plane Region Insights Investigation Guide** dashboard, chapter **Release** (5 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## (no subgroup)

### CRP Release

_Widget purpose:_ Release

Cluster: `aegisfollower.centralus.kusto.windows.net` · Database: `gandalf_tdpr` · Type: `Timeline`
Source panel: `Release`

```kusto
_CCEComponentDeployments
    | where Component == "CRP"
        and FirstDeploymentDetectedTime between (startTime..endTime)
        and DeploymentUnitType == "region"
    | summarize arg_max(RunTime, FirstDeploymentDetectedTime, LastDeploymentDetectedTime)
        by Component, DeploymentUnitType, DeploymentUnit, ServiceBuild
    | where DeploymentUnit == tolower(replace_string(region, ' ', ""))
    | project
        Service=Component,
        Content=ServiceBuild,
        StartTime=FirstDeploymentDetectedTime,
        EndTime=LastDeploymentDetectedTime
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `Component == "CRP"`

---

### NRP Release

_Widget purpose:_ Release

Cluster: `aegisfollower.centralus.kusto.windows.net` · Database: `gandalf_tdpr` · Type: `Timeline`
Source panel: `Release`

```kusto
_CCEComponentDeployments
    | where Component == "NRP"
        and FirstDeploymentDetectedTime between (startTime..endTime)
        and DeploymentUnitType == "region"
    | summarize arg_max(RunTime, FirstDeploymentDetectedTime, LastDeploymentDetectedTime)
        by Component, DeploymentUnitType, DeploymentUnit, ServiceBuild
    | where DeploymentUnit == tolower(replace_string(region, ' ', "")) and DeploymentUnit !contains "validation"
    | project
        Service=Component,
        Content=ServiceBuild,
        StartTime=FirstDeploymentDetectedTime,
        EndTime=LastDeploymentDetectedTime
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `Component == "NRP"`

---

### AKS Release

_Widget purpose:_ Release

Cluster: `https://aegisfollower.centralus.kusto.windows.net` · Database: `gandalf_tdpr` · Type: `Timeline`
Source panel: `Release`

```kusto
_CCEComponentDeployments
    | where Component == "AKSRP"
        and FirstDeploymentDetectedTime between (startTime..endTime)
        and DeploymentUnitType == "region"
    | summarize arg_max(RunTime, FirstDeploymentDetectedTime, LastDeploymentDetectedTime)
        by Component, DeploymentUnitType, DeploymentUnit, ServiceBuild
    | where DeploymentUnit == tolower(replace_string(region, ' ', ""))
    | project
        Service=Component,
        Content=ServiceBuild,
        StartTime=FirstDeploymentDetectedTime,
        EndTime=LastDeploymentDetectedTime
```

**Params:** `{startTime}`, `{endTime}`, `{region}`

**Signal filters seen in KQL:** `Component == "AKSRP"`

---

### ARM Release

_Widget purpose:_ Release

Cluster: `gandalfcontrolplane.kusto.windows.net` · Database: `arm_analytics` · Type: `Timeline`
Source panel: `Release`

```kusto
ARM_DeploymentEvent_Data(startTime=startTime, endTime=endTime)
| where tolower(replace_string(RoleLocation, ' ', "")) == tolower(replace_string(region, ' ', ""))
| project
        Service="ARM",
        StartTime=DeploymentTime,
        EndTime=DeploymentTime,
        Content=strcat(Role, " ",ReleaseVersion)
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

---

### Release

Cluster: `gandalfcontrolplane.kusto.windows.net` · Database: `arm_analytics` · Type: `Table`
Source panel: `Release`

```kusto
let arm = ARM_DeploymentEvent_Data(startTime=startTime, endTime=endTime)
| where tolower(replace_string(RoleLocation, ' ', "")) == tolower(replace_string(region, ' ', ""))
| project
        Service="ARM",
        FirstDeploymentDetectedTime=tostring(DeploymentTime),
        Role,
        ReleaseVersion;
let crp = 
    cluster("https://aegisfollower.centralus.kusto.windows.net").database("gandalf_tdpr")._CCEComponentDeployments
    | where Component == "CRP"
        and FirstDeploymentDetectedTime between (startTime..endTime)
        and DeploymentUnitType == "region"
    | summarize arg_max(RunTime, FirstDeploymentDetectedTime, LastDeploymentDetectedTime)
        by Component, DeploymentUnitType, DeploymentUnit, ServiceBuild
    | where DeploymentUnit == tolower(replace_string(region, ' ', ""))
    | project
        Service=Component,
        ReleaseVersion=ServiceBuild,
        FirstDeploymentDetectedTime=tostring(FirstDeploymentDetectedTime),
        LastDeploymentDetectedTime=tostring(LastDeploymentDetectedTime);
    let nrp = 
    cluster("https://aegisfollower.centralus.kusto.windows.net").database("gandalf_tdpr")._CCEComponentDeployments
    | where Component == "NRP"
        and FirstDeploymentDetectedTime between (startTime..endTime)
        and DeploymentUnitType == "region"
    | summarize arg_max(RunTime, FirstDeploymentDetectedTime, LastDeploymentDetectedTime)
        by Component, DeploymentUnitType, DeploymentUnit, ServiceBuild
    | where DeploymentUnit == tolower(replace_string(region, ' ', "")) and DeploymentUnit !contains "validation"
    | project
        Service=Component,
        ReleaseVersion=ServiceBuild,
        FirstDeploymentDetectedTime=tostring(FirstDeploymentDetectedTime),
        LastDeploymentDetectedTime=tostring(LastDeploymentDetectedTime);
let aks = 
    cluster("https://aegisfollower.centralus.kusto.windows.net").database("gandalf_tdpr")._CCEComponentDeployments
    | where Component == "AKSRP"
        and FirstDeploymentDetectedTime between (startTime..endTime)
        and DeploymentUnitType == "region"
    | summarize arg_max(RunTime, FirstDeploymentDetectedTime, LastDeploymentDetectedTime)
        by Component, DeploymentUnitType, DeploymentUnit, ServiceBuild
    | where DeploymentUnit == tolower(replace_string(region, ' ', ""))
    | project
        Service=Component,
        ReleaseVersion=ServiceBuild,
        FirstDeploymentDetectedTime=tostring(FirstDeploymentDetectedTime);
union crp, nrp, arm, aks
```

**Params:** `{region}`, `{startTime}`, `{endTime}`

**Signal filters seen in KQL:** `Component == "CRP"` · `Component == "NRP"` · `Component == "AKSRP"`

---
