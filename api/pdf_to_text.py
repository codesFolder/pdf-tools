# api/pdf_to_text.py

from http.server import BaseHTTPRequestHandler
import json
import cgi
import fitz  # PyMuPDF

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            # 1. Parse the multipart/form-data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type']}
            )
            
            # 2. Check if the file was uploaded
            if 'pdf_file' not in form:
                self.send_error(400, "No file uploaded")
                return

            file_item = form['pdf_file']
            
            # 3. Read the file content
            if file_item.file:
                pdf_bytes = file_item.file.read()
                
                # 4. Process the PDF with PyMuPDF
                full_text = ""
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                    for page in doc:
                        full_text += page.get_text()
                
                # 5. Send a success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'success': True,
                    'text': full_text
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_error(400, "Uploaded file has no content")

        except Exception as e:
            # 6. Send an error response if anything goes wrong
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                'success': False,
                'error': f"An error occurred: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))