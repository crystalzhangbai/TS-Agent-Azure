# Info

> Source: **Azure Subscription Investigation Guide** dashboard, chapter **Info** (1 queries across 1 sub-groups).

Each KQL block is preserved verbatim from the dashboard. Substitute params (`{globalFrom}`, `{nodeId}`, etc.) with case values, then execute via vm-kusto-query / kusto_runner.py / replay.py.

---

## Subscription Details

### SubscriptionDetails

_Widget purpose:_ Subscription Details

Cluster: `datastudiostreaming` · Database: `Shared` · Type: `Single` · Widget: `Card`
Source panel: `Info > Subscription Details`

```kusto
let subscriptionSnapshotDataStudio = cluster('datastudiostreaming').database('Shared').DataStudio_AzureSubscription_Snapshot
| where SubscriptionId in~ (subId)
| distinct SubscriptionId, SubscriptionName, SubscriptionState, CustomerName, PCCode, CostCategory, AzureSpendSTPath, AccountAdmin, ServiceTreeName = STName, ServiceTreeId = STId;
let subscriptionSnapshotCustomerDomData = cluster('customerdomrptwus3prod.westus3').database('CustomerDomData').CustomerModel
| where SubscriptionGuid_String in~ (subId)
| distinct SubscriptionId = SubscriptionGuid_String, SubscriptionName = FriendlySubscriptionName, SubscriptionState = CurrentSubscriptionStatus, CloudCustomerName, TPName = TPNameTranslated, OfferName, OfferType, OfferId;
union subscriptionSnapshotDataStudio, subscriptionSnapshotCustomerDomData
| summarize take_anyif(SubscriptionName, isnotempty(SubscriptionName)), 
            take_anyif(SubscriptionState, isnotempty(SubscriptionState)), 
            take_anyif(CustomerName, isnotempty(CustomerName)), 
            take_anyif(CloudCustomerName, isnotempty(CloudCustomerName)), 
            take_anyif(TPName, isnotempty(TPName)), 
            take_anyif(OfferName, isnotempty(OfferName)), 
            take_anyif(OfferType, isnotempty(OfferType)), 
            take_anyif(OfferId, isnotempty(OfferId)), 
            take_anyif(PCCode, isnotempty(PCCode)), 
            take_anyif(CostCategory, isnotempty(CostCategory)), 
            take_anyif(AzureSpendSTPath, isnotempty(AzureSpendSTPath)), 
            take_anyif(AccountAdmin, isnotempty(AccountAdmin)), 
            take_anyif(ServiceTreeName, isnotempty(ServiceTreeName)), 
            take_anyif(ServiceTreeId, isnotempty(ServiceTreeId))
            by SubscriptionId
```

**Params:** `{queryFrom}`, `{queryTo}`, `{subId}`

---
