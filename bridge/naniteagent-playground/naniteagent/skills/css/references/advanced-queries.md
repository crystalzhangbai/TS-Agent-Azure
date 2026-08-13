# Advanced Query Scenarios

### Cross-Reference User and Device Information
```kql
// Get user details with their assigned devices
let userInfo = AADUser | where UserPrincipalName contains "alias" | project UserAlias=UserPrincipalName, DisplayName, Department;
let deviceInfo = EmployeeDevice | where EmployeeAlias in ((userInfo | project UserAlias));
userInfo | join kind=inner deviceInfo on $left.UserAlias == $right.EmployeeAlias
```

### Organizational Device Distribution
```kql
// Analyze device distribution across organizational units
People_Person
| join kind=inner (EmployeeDevice | where AssetStatus == "Active") on $left.PersonAlias == $right.EmployeeAlias
| summarize DeviceCount=count() by Organization, DeviceType
| order by Organization, DeviceCount desc
```
