// lib/main.dart
import 'package:flutter/material.dart';
import 'package:pedhaaap/home_page.dart';

void main() {
  runApp(const ConsultancyHiringToolApp());
}

class ConsultancyHiringToolApp extends StatelessWidget {
  const ConsultancyHiringToolApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Consultancy Firm Hiring Tool',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: HomePage(),
    );
  }
}
