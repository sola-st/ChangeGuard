import json

with open('../annotated_changes/annotated_changes_old.json') as f:
    annotated_changes = json.load(f)

preserving_changes = [change for change in annotated_changes if change['annotation'] == 'semantics_preserving']
changing_changes = [change for change in annotated_changes if change['annotation'] == 'semantics_changing']
print('Num Semantics_Preserving:', len(preserving_changes), 'Num Semantics_Changing:', len(changing_changes))
source_refactor = [change for change in annotated_changes if change['source'] == 'refactor']
source_change = [change for change in annotated_changes if change['source'] == 'change']
print('Num Source_Refactor:', len(source_refactor), 'Num Source_Change:', len(source_change))
incorrect_source_refactor = [change for change in source_refactor if change['annotation'] == 'semantics_changing']
incorrect_source_change = [change for change in source_change if change['annotation'] == 'semantics_preserving']
print('Num Incorrect_Refactor:', len(incorrect_source_refactor), 'Num Incorrect_Change:', len(incorrect_source_change))
pandas_preserving = [change for change in annotated_changes if change['annotation'] == 'semantics_preserving' and change['repo'] == 'pandas']
pandas_total = [change for change in annotated_changes if change['repo'] == 'pandas']
print('Pandas Total:', len(pandas_total), 'Pandas Preserving:', len(pandas_preserving))

