import { useState, useRef } from 'react'
import { FileText, Image as ImageIcon, CheckCircle, Download, Loader2, X } from 'lucide-react'
import axios from 'axios'

function App() {
  const [ocrFile, setOcrFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [step, setStep] = useState(1)
  const [taskId, setTaskId] = useState<string | null>(null)
  const activeTaskRef = useRef<string | null>(null)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1'

  const [ocrResults, setOcrResults] = useState<any[] | null>(null)

  const handleUnselect = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setOcrFile(null)
  }

  const pollStatus = async (id: string) => {
    try {
      if (activeTaskRef.current !== id) return

      const response = await axios.get(`${API_URL}/ocr/status/${id}`)
      const { status, progress, result_data, error: apiError } = response.data

      if (activeTaskRef.current !== id) return

      setProgress(progress)

      if (status === 'completed') {
        setOcrResults(result_data || [])
        setLoading(false)
        setStep(2)
        downloadFile(id)
      } else if (status === 'failed') {
        setLoading(false)
        alert(`OCR Failed: ${apiError}`)
        // Add a diagnostic hint
        console.error("Diagnostic: If this persists, the file might be corrupted. Check local 'backend/uploads/failing_file.bin'")
      } else {
        setTimeout(() => pollStatus(id), 1000)
      }
    } catch (error) {
      if (activeTaskRef.current === id) {
        console.error('Polling Error:', error)
        setLoading(false)
        alert('Error tracking OCR progress.')
      }
    }
  }

  const handleCancel = () => {
    activeTaskRef.current = null
    setTaskId(null)
    setLoading(false)
    setProgress(0)
  }

  const downloadFile = async (id: string) => {
    try {
      const response = await axios.get(`${API_URL}/ocr/download/${id}`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `scanned_${ocrFile?.name || 'result'}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Download Error:', error)
    }
  }

  const handleScanToPdf = async () => {
    if (!ocrFile) return
    setLoading(true)
    setProgress(0)
    
    try {
      // Create a clean binary blob from the file to ensure no encoding issues
      const fileBlob = new Blob([ocrFile], { type: ocrFile.type })
      const formData = new FormData()
      formData.append('file', fileBlob, ocrFile.name)
      
      const response = await axios.post(`${API_URL}/ocr/scan-to-pdf-async`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      const { task_id } = response.data
      setTaskId(task_id)
      activeTaskRef.current = task_id
      pollStatus(task_id)
    } catch (error) {
      console.error('Scan Error:', error)
      setLoading(false)
      alert('Failed to start OCR process.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-8">
      <header className="max-w-4xl mx-auto mb-12">
        <h1 className="text-4xl font-bold text-indigo-600 flex items-center gap-3">
          <FileText size={40} />
          Scan to Searchable PDF
        </h1>
        <p className="text-gray-600 mt-2">Upload a document image to extract text and generate a PDF version.</p>
      </header>

      <main className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-8">
        <div className="flex justify-center mb-8 border-b pb-4">
          <div className={`flex items-center gap-2 ${step >= 1 ? 'text-indigo-600 font-bold' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${step >= 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'}`}>
              1
            </div>
            <span>Upload Image</span>
          </div>
          <div className="w-20 border-t-2 mt-4 mx-4 border-gray-200"></div>
          <div className={`flex items-center gap-2 ${step >= 2 ? 'text-indigo-600 font-bold' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${step >= 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'}`}>
              2
            </div>
            <span>Download PDF</span>
          </div>
        </div>

        {step === 1 && (
          <div className="space-y-6">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-indigo-400 transition-colors">
              <ImageIcon className="mx-auto text-gray-400 mb-4" size={48} />
              <input 
                type="file" 
                onChange={(e) => setOcrFile(e.target.files?.[0] || null)}
                className="hidden" 
                id="ocr-upload"
              />
              <label htmlFor="ocr-upload" className="cursor-pointer text-indigo-600 font-semibold hover:underline flex items-center justify-center gap-2 group">
                {ocrFile ? ocrFile.name : 'Select any file for scanning'}
                {ocrFile && (
                  <button 
                    onClick={handleUnselect}
                    className="p-1 hover:bg-gray-100 rounded-full text-gray-400 hover:text-red-500 transition-colors"
                    title="Unselect file"
                  >
                    <X size={16} />
                  </button>
                )}
              </label>
              {ocrFile && (
                <p className="text-xs text-gray-400 mt-1">
                  Type: {ocrFile.type || 'unknown'} | Size: {(ocrFile.size / 1024).toFixed(1)} KB
                </p>
              )}
              <p className="text-sm text-gray-500 mt-2">All formats allowed (Images, PDFs, etc.)</p>
            </div>
            
            {loading && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm font-medium">
                    <span>Processing document...</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
                <button 
                  onClick={handleCancel}
                  className="text-red-500 text-sm font-semibold hover:text-red-700 w-full text-center"
                >
                  Cancel Process
                </button>
              </div>
            )}

            <button 
              onClick={handleScanToPdf}
              disabled={!ocrFile || loading}
              className="w-full bg-indigo-600 text-white py-4 rounded-lg font-bold hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center gap-2 text-lg"
            >
              {loading && <Loader2 className="animate-spin" />}
              {loading ? `Processing OCR (${progress}%)...` : 'Generate Scanned PDF'}
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="text-center py-12 space-y-6">
            <div className="bg-green-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto text-green-600">
              <CheckCircle size={48} />
            </div>
            <h2 className="text-2xl font-bold">PDF Generated!</h2>
            <p className="text-gray-600">Your scanned document is ready and downloading.</p>

            {ocrResults && ocrResults.length > 0 && (
              <div className="mt-8 text-left border rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-4 py-2 border-b font-semibold text-sm text-gray-700">
                  Extracted Text Preview
                </div>
                <div className="max-h-64 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-100 sticky top-0">
                      <tr>
                        <th className="px-4 py-2 text-left">Text</th>
                        <th className="px-4 py-2 text-right">Confidence</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {ocrResults.map((res, i) => (
                        <tr key={i} className="hover:bg-gray-50">
                          <td className="px-4 py-2">{res.text}</td>
                          <td className="px-4 py-2 text-right">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              res.confidence > 0.8 ? 'bg-green-100 text-green-700' : 
                              res.confidence > 0.5 ? 'bg-yellow-100 text-yellow-700' : 
                              'bg-red-100 text-red-700'
                            }`}>
                              {(res.confidence * 100).toFixed(1)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="flex gap-4 justify-center">
              <button 
                onClick={() => setStep(1)}
                className="bg-gray-200 text-gray-800 px-8 py-3 rounded-lg hover:bg-gray-300 font-semibold"
              >
                Scan Another
              </button>
              <button 
                onClick={() => taskId && downloadFile(taskId)}
                className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 flex items-center gap-2 font-semibold"
              >
                <Download size={20} />
                Download Again
              </button>
            </div>
          </div>
        )}
      </main>
      
      <footer className="mt-12 text-center text-gray-400 text-sm">
        OCR Scan-to-PDF Engine &copy; 2026
      </footer>
    </div>
  )
}

export default App
