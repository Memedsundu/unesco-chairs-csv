# UNESCO Chairs CSV

Daily list of active UNITWIN/UNESCO Chairs for the CPD001 KoboToolbox form.

The source is the public UNESCO DataHub dataset [`fli001`](https://data.unesco.org/explore/assets/fli001/). A GitHub Action downloads it every day at 06:00 UTC and commits `unesco_chairs.csv` when a Chair has been added or removed.

## KoboToolbox

In the form project, open **SETTINGS → Media** and add this URL:

```text
https://raw.githubusercontent.com/Memedsundu/unesco-chairs-csv/main/unesco_chairs.csv
```

The form question must reference the filename `unesco_chairs.csv`. After the Action commits a change, redeploy the form so respondents receive the updated list.

## Run it now

Actions → **Update UNESCO Chairs** → **Run workflow**.
