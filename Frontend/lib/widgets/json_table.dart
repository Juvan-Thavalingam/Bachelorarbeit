import 'package:flutter/material.dart';

class JsonTable extends StatefulWidget {
  final List<Map<String, dynamic>> data;
  final double maxHeight;

  const JsonTable({super.key, required this.data, this.maxHeight = 1000});

  @override
  _JsonTableState createState() => _JsonTableState();
}

class _JsonTableState extends State<JsonTable> {
  int currentPage = 0;
  final int rowsPerPage = 10;
  final ScrollController _horizontalScrollController = ScrollController();

  @override
  void dispose() {
    _horizontalScrollController.dispose();
    super.dispose();
  }

  @override
Widget build(BuildContext context) {
  if (widget.data.isEmpty) return const Text("Keine Daten vorhanden.");

  int totalPages = (widget.data.length / rowsPerPage).ceil();
  int start = currentPage * rowsPerPage;
  int end = (start + rowsPerPage).clamp(0, widget.data.length);
  List<Map<String, dynamic>> currentData = widget.data.sublist(start, end);

  final columns = widget.data.first.keys.toList();

  return Column(
    children: [
      ConstrainedBox(
        constraints: BoxConstraints(maxHeight: widget.maxHeight),
        child: Scrollbar(
          controller: _horizontalScrollController,
          thumbVisibility: true,
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            controller: _horizontalScrollController,
            child: IntrinsicWidth(
              child: DataTable(
                columns: columns.map((col) => DataColumn(
                  label: Text(col + ":", style: const TextStyle(fontWeight: FontWeight.bold)),
                )).toList(),
                rows: currentData.map((row) => DataRow(
                  cells: columns.map((col) => DataCell(
                    Text(row[col]?.toString() ?? "-"),
                  )).toList(),
                )).toList(),
              ),
            ),
          ),
        ),
      ),
      const SizedBox(height: 10),
      Text("Seite ${currentPage + 1} von $totalPages"),
      const SizedBox(height: 10),
      Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          ElevatedButton(
            onPressed: currentPage > 0
                ? () => setState(() => currentPage--)
                : null,
            child: const Text("Zurück"),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: currentPage < totalPages - 1
                ? () => setState(() => currentPage++)
                : null,
            child: const Text("Weiter"),
          ),
        ],
      ),
    ],
  );
}


}