import { useState, useRef } from 'react'
import { FileText, Image as ImageIcon, CheckCircle, Download, X, UploadCloud } from 'lucide-react'
import axios from 'axios'

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [step, setStep] = useState(1) // 1: Upload, 2: Result
  const [taskId, setTaskId] = useState<string | null>(null)
  const [ocrResults, setOcrResults] = useState<any[] | null>(null)
  const activeTaskRef = useRef<string | null>(null)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1'

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0] || null
    setFile(selectedFile)
  }

  const handleUnselect = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setFile(null)
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
      } else {
        setTimeout(() => pollStatus(id), 1000)
      }
    } catch (error) {
      if (activeTaskRef.current === id) {
        setLoading(false)
        alert('Error connecting to processing engine.')
      }
    }
  }

  const downloadFile = async (id: string) => {
    try {
      const response = await axios.get(`${API_URL}/ocr/download/${id}`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `scanned_${file?.name.split('.')[0] || 'result'}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download error:', error)
    }
  }

  const handleStartProcessing = async () => {
    if (!file) return
    setLoading(true)
    setProgress(0)
    
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      const response = await axios.post(`${API_URL}/ocr/scan-to-pdf-async`, formData)
      const { task_id } = response.data
      setTaskId(task_id)
      activeTaskRef.current = task_id
      pollStatus(task_id)
    } catch (error) {
      setLoading(false)
      alert('Failed to start OCR process. Please check your connection.')
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-100 selection:text-indigo-700">
      {/* Navbar */}
      <nav className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2 text-indigo-600">
            <FileText size={28} strokeWidth={2.5} />
            <span className="text-xl font-black tracking-tight uppercase">SmartScan OCR</span>
          </div>
          <div className="hidden sm:block text-xs font-bold text-slate-400 tracking-widest uppercase">
            Production Ready v1.0
          </div>
        </div>
      </nav>

      <main className="max-w-2xl mx-auto px-6 py-12 md:py-20">
        {step === 1 ? (
          <div className="space-y-8 animate-in fade-in duration-500">
            <div className="text-center space-y-2">
              <h1 className="text-4xl font-black tracking-tight text-slate-900">Universal OCR Engine</h1>
              <p className="text-slate-500 text-lg">Convert any Image, PDF, or Word document into a searchable PDF.</p>
            </div>

            {/* Upload Area */}
            <div className={`relative group transition-all duration-300 ${loading ? 'opacity-50 pointer-events-none' : ''}`}>
              <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-blue-600 rounded-3xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
              <div className="relative bg-white border-2 border-dashed border-slate-200 rounded-3xl p-10 md:p-16 text-center hover:border-indigo-400 transition-all">
                <input 
                  type="file" 
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
                  disabled={loading}
                />
                
                {!file ? (
                  <div className="space-y-4">
                    <div className="w-20 h-20 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto group-hover:scale-110 transition-transform duration-300">
                      <UploadCloud size={40} />
                    </div>
                    <div>
                      <p className="text-xl font-bold text-slate-800">Click or drag file to upload</p>
                      <p className="text-slate-400 mt-1">Supports JPG, PNG, PDF, and DOCX</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4 animate-in zoom-in duration-300">
                    <div className="w-20 h-20 bg-green-50 text-green-600 rounded-2xl flex items-center justify-center mx-auto">
                      <ImageIcon size={40} />
                    </div>
                    <div>
                      <div className="flex items-center justify-center gap-2">
                        <p className="text-xl font-bold text-slate-800 truncate max-w-[250px]">{file.name}</p>
                        <button 
                          onClick={handleUnselect}
                          className="p-1 hover:bg-red-50 text-slate-400 hover:text-red-500 rounded-full transition-colors relative z-20"
                        >
                          <X size={20} />
                        </button>
                      </div>
                      <p className="text-indigo-600 font-bold mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Action Area */}
            <div className="space-y-4">
              {loading ? (
                <div className="space-y-4 bg-white p-6 rounded-2xl border border-slate-100 shadow-sm animate-in slide-in-from-bottom-4 duration-500">
                  <div className="flex justify-between items-end">
                    <div className="space-y-1">
                      <p className="text-sm font-black text-slate-900 uppercase tracking-wider">Processing OCR</p>
                      <p className="text-xs text-slate-400 font-bold">Please don't close this window...</p>
                    </div>
                    <span className="text-2xl font-black text-indigo-600">{Math.round(progress)}%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                    <div 
                      className="bg-indigo-600 h-full transition-all duration-500 ease-out shadow-[0_0_15px_rgba(79,70,229,0.4)]" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                  <button 
                    onClick={() => { activeTaskRef.current = null; setLoading(false); }}
                    className="w-full py-2 text-sm font-bold text-red-400 hover:text-red-600 transition-colors"
                  >
                    Cancel Task
                  </button>
                </div>
              ) : (
                <button 
                  onClick={handleStartProcessing}
                  disabled={!file}
                  className="w-full bg-indigo-600 text-white py-5 rounded-2xl font-black text-xl shadow-xl shadow-indigo-200 hover:bg-indigo-700 hover:-translate-y-1 active:translate-y-0.5 transition-all disabled:opacity-50 disabled:pointer-events-none"
                >
                  Start Searchable PDF Scan
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center space-y-10 animate-in fade-in zoom-in duration-500">
            <div className="space-y-4">
              <div className="w-24 h-24 bg-green-50 text-green-600 rounded-full flex items-center justify-center mx-auto shadow-inner">
                <CheckCircle size={56} strokeWidth={2.5} />
              </div>
              <div className="space-y-2">
                <h2 className="text-4xl font-black text-slate-900">Success!</h2>
                <p className="text-slate-500 text-lg">Your high-accuracy searchable PDF is ready.</p>
              </div>
            </div>

            {/* Extraction Preview */}
            {ocrResults && ocrResults.length > 0 && (
              <div className="text-left border border-slate-200 rounded-3xl overflow-hidden bg-white shadow-sm">
                <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                  <span className="font-black text-xs uppercase tracking-widest text-slate-500">Extraction Preview</span>
                  <span className="text-xs font-bold bg-green-100 text-green-700 px-2 py-1 rounded">High Accuracy</span>
                </div>
                <div className="max-h-48 overflow-y-auto p-4">
                  <div className="flex flex-wrap gap-2">
                    {ocrResults.slice(0, 30).map((res, i) => (
                      <span key={i} className="text-sm bg-slate-50 px-2 py-1 rounded border border-slate-100 text-slate-600">
                        {res.text}
                      </span>
                    ))}
                    {ocrResults.length > 30 && <span className="text-slate-300 text-sm italic">...and {ocrResults.length - 30} more blocks</span>}
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <button 
                onClick={() => { setStep(1); setFile(null); setOcrResults(null); }}
                className="py-5 rounded-2xl font-black text-lg bg-slate-100 text-slate-600 hover:bg-slate-200 transition-all"
              >
                Scan Another
              </button>
              <button 
                onClick={() => taskId && downloadFile(taskId)}
                className="py-5 rounded-2xl font-black text-lg bg-indigo-600 text-white shadow-xl shadow-indigo-100 hover:bg-indigo-700 transition-all flex items-center justify-center gap-2"
              >
                <Download size={24} />
                Download PDF
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="max-w-2xl mx-auto px-6 py-12 text-center border-t border-slate-100">
        <p className="text-slate-400 text-sm font-bold uppercase tracking-widest">&copy; 2026 Accurate OCR Intelligence Engine</p>
      </footer>
    </div>
  )
}

export default App
