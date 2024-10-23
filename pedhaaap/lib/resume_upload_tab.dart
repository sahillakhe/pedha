// lib/resume_upload_tab.dart
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

class ResumeUploadTab extends StatefulWidget {
  const ResumeUploadTab({super.key});

  @override
  ResumeUploadTabState createState() => ResumeUploadTabState();
}

class ResumeUploadTabState extends State<ResumeUploadTab> {
  List<PlatformFile>? _files;

  void _pickFiles() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      allowedExtensions: ['pdf', 'docx'],
      allowMultiple: true,
      type: FileType.custom,
    );

    if (result != null) {
      setState(() {
        _files = result.files;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          const Text(
            'Batch PDF Embedding Saver',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _pickFiles,
            child: const Text('Select Resumes'),
          ),
          const SizedBox(height: 16),
          _files != null
              ? Expanded(
                  child: ListView.builder(
                    itemCount: _files!.length,
                    itemBuilder: (context, index) {
                      return ListTile(
                        title: Text(_files![index].name),
                      );
                    },
                  ),
                )
              : const Text('No files selected.'),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              // Placeholder for upload functionality
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                    content: Text('Upload functionality not implemented.')),
              );
            },
            child: const Text('Upload Resumes'),
          ),
        ],
      ),
    );
  }
}
