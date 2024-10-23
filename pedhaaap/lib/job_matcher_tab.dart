// lib/job_matcher_tab.dart
import 'package:flutter/material.dart';

class JobMatcherTab extends StatefulWidget {
  const JobMatcherTab({super.key});

  @override
  JobMatcherTabState createState() => JobMatcherTabState();
}

class JobMatcherTabState extends State<JobMatcherTab> {
  final TextEditingController _jobDescriptionController =
      TextEditingController();
  bool _isLoading = false;
  List<Map<String, dynamic>> _results = [];

  void _evaluateCandidates() async {
    setState(() {
      _isLoading = true;
      _results = [];
    });

    // Placeholder for backend call
    await Future.delayed(const Duration(seconds: 2)); // Simulate a network call

    setState(() {
      _isLoading = false;
      _results = [
        {
          'filename': 'resume1.pdf',
          'score': 98.5,
          'explanation':
              'Candidate has extensive experience in Python development.'
        },
        {
          'filename': 'resume2.pdf',
          'score': 95.0,
          'explanation': 'Candidate matches the job requirements closely.'
        },
      ];
    });
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Job Matcher',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          const Text('Enter the job description:'),
          const SizedBox(height: 8),
          TextField(
            controller: _jobDescriptionController,
            maxLines: 5,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              hintText: 'Type the job description here...',
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _evaluateCandidates,
            child: const Text('Evaluate Candidates'),
          ),
          const SizedBox(height: 16),
          _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _results.isNotEmpty
                  ? Expanded(
                      child: ListView.builder(
                        itemCount: _results.length,
                        itemBuilder: (context, index) {
                          var result = _results[index];
                          return Card(
                            child: ListTile(
                              title: Text(result['filename']),
                              subtitle: Text(
                                  'Score: ${result['score']}\nExplanation: ${result['explanation']}'),
                            ),
                          );
                        },
                      ),
                    )
                  : const Text('No results to display.'),
        ],
      ),
    );
  }
}
