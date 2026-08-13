# Known Page IDs — SUSE SAP / Linux Clustering

Wiki pages commonly referenced when troubleshooting SUSE HA / SAP HANA on Azure VM. These `pageId`s have been verified in past cases and are cached here to **save one `csswiki-search_wiki` + `list_pages` round-trip**: when the main flow detects SUSE / SAP keywords, the LLM can build the URL directly for the customer, or feed the `pageId` straight into `csswiki-wiki(action="get_page", wikiIdentifier="AzureLinuxNinjas", pageId=<id>)` to fetch content in one call.

If the page isn't listed here, fall back to the standard csswiki search flow (see SKILL.md §3 Step 3).

---

## AzureIaaSVM Wiki (csswiki Project Wiki)

| Page | Page ID | URL |
|------|---------|-----|
| Internal error - MachineKeys_RDP-SSH | 758780 | `https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/758780/Internal-error-MachineKeys_RDP-SSH` |
| Internal error - TLS Events_RDP-SSH | 758784 | `https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/758784/Internal-error-TLS-Events_RDP-SSH` |
| Internal error - SSL Cipher Suite | 758782 | `https://supportability.visualstudio.com/AzureIaaSVM/_wiki/wikis/AzureIaaSVM/758782/Internal-error-SSL-Cipher-Suite-Events_RDP-SSH` |

---

## AzureLinuxNinjas Wiki (csswiki Code Wiki) — SUSE SAP HANA & Clustering

> **Base URL**: `https://supportability.visualstudio.com/AzureLinuxNinjas/_wiki/wikis/AzureLinuxNinjas/{pageId}`
> **Wiki ID**: `cd4da838-44e4-4b34-b872-a3fe42c973c8`
> **Wiki type**: Code Wiki (Git-backed; search paths use hyphens, actual paths use spaces)
> **Path prefix**: all pages live under `/GeneralPages/Azure/TGs/Azure Linux Clustering/SUSE SAP HANA and Clustering/`

| Page | Page ID |
|------|---------|
| SAP & Clustering Homepage | 214335 |
| How to configure Pacemaker cluster on SUSE VM with SBD fencing | 214340 |
| How to configure Pacemaker cluster on SUSE VM with Azure fencing agent | 214370 |
| Azure Fencing Agent: Resource Start-up Issues | 311339 |
| How to troubleshoot Pacemaker fencing issue exit code 100 | 326700 |
| SAP health check errors or trace entry or log alert about TSC timing information | 374740 |
| Azure Fence Agent details and troubleshooting | 486271 |
| How to fix SAP HANA Start Failures | 491971 |
| Cluster Troubleshooting TSG | 504070 |
| How to patch or update packages in SUSE cluster | 514295 |
| Azure Fence Agent not starting after SLES Patching or Migration | 520616 |
| Failover of ASCS ERS cluster not happening due to bug with psmisc package | 522701 |
| Failover Delay in NFS Cluster due to NFS4 Lease time | 537097 |
| Limitations for health probe failure in SUSE SAP clustering | 214356 |
| Steps to Troubleshoot NFS mount hang after configuring NFS cluster SUSE | 284291 |
| Steps and scope to replace nc with socat on SUSE HA cluster configuration | 297962 |

---

## Usage

When the main flow matches any of the following keywords, **look up this table → build the URL directly** (saves one csswiki round-trip):

- SUSE / SLES / SAP / HANA / Pacemaker / SBD / fence agent / corosync / cluster failover
- RDP internal error / MachineKeys / TLS Events / SSL Cipher Suite (the three AzureIaaSVM entries above)

If the user's specific symptom is not in this table, **fall back to the standard csswiki search** (see SKILL.md §3 Step 3).
