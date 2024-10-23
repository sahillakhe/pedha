// lib/home_page.dart
import 'package:flutter/material.dart';
import 'package:pedhaaap/job_matcher_tab.dart';
import 'package:pedhaaap/resume_upload_tab.dart';

class HomePage extends StatelessWidget {
  final List<Tab> myTabs = <Tab>[
    const Tab(text: 'Resume Upload'),
    const Tab(text: 'Job Matcher'),
  ];

  HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: myTabs.length,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Consultancy Firm Hiring Tool'),
          bottom: TabBar(
            tabs: myTabs,
          ),
        ),
        body: const TabBarView(
          children: [
            ResumeUploadTab(),
            JobMatcherTab(),
          ],
        ),
      ),
    );
  }
}
