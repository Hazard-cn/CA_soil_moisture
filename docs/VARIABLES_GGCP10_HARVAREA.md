# GGCP10 harvest-area branch variables

| Variable | Definition | Unit |
|----------|------------|------|
| `ggcp10_harvarea_thousand_ha` | Raw sampled GGCP10 maize harvested area | thousand ha |
| `ggcp10_maize_area_km2` | GGCP10 maize harvested area after unit conversion | km2 |
| `maize_area_km2` | Branch replacement of maize area using GGCP10 harvested area | km2 |
| `ggcp10_maize_frac` | `maize_area_km2 / pixel_area_km2` | 0-1 |
| `maize_prod` | Original maize production merged from the master source table | source unit |
| `maize_yield_km2` | `maize_prod / maize_area_km2` | production per km2 |
| `yield_tons_ha` | `maize_yield_km2 * 10` | tons/ha |
| `ln_yield` | `ln(yield_tons_ha)` | log tons/ha |
| `orig_maize_area_km2` | Pre-branch area value retained for comparison | km2 |
| `orig_yield_tons_ha` | Pre-branch yield value retained for comparison | tons/ha |
| `orig_ln_yield` | Pre-branch log yield retained for comparison | log tons/ha |
| `orig_main_sample` | Main-sample flag before GGCP10 replacement | 0/1 |
| `ggcp10_harvarea_valid` | Positive-area and valid-yield flag after GGCP10 replacement | 0/1 |
