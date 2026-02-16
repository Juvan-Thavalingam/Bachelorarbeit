import 'package:flutter/material.dart';

class Filter_Checkbox extends StatelessWidget {
  final Map<String, bool> filterSelections;
  final Function(String, bool) onChanged;

  const Filter_Checkbox({
    Key? key,
    required this.filterSelections,
    required this.onChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 60, // etwas mehr Platz für CheckboxListTile
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: filterSelections.entries.map((entry) {
          return Container(
            constraints: const BoxConstraints(minWidth: 50, maxWidth: 180),
            margin: const EdgeInsets.symmetric(horizontal: 6), // Abstand zwischen Checkboxen
            child: CheckboxListTile(
              contentPadding: EdgeInsets.zero,
              title: Text(
                entry.key,
                softWrap: false,
                overflow: TextOverflow.ellipsis,
              ),
              value: entry.value,
              onChanged: (bool? newValue) {
                onChanged(entry.key, newValue ?? false);
              },
            ),
          );
        }).toList(),
      ),
    );
  }
}
