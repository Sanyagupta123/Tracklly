import { useEffect, useMemo, useState } from 'react'
import {
  analyzeDescription,
  createApplication,
  deleteApplication,
  fetchApplications,
  updateApplication,
} from './api'
import './App.css'

const initialForm = {
  company: '',
  role: '',
  job_description: '',
  status: 'Applied',
}

const statusOptions = ['Wishlist', 'Applied', 'Interview', 'Offer', 'Rejected']

function App() {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [form, setForm] = useState(initialForm)
  const [formErrors, setFormErrors] = useState({})
  const [isEditing, setIsEditing] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [saving, setSaving] = useState(false)
  const [analysisText, setAnalysisText] = useState('')
  const [analysisResult, setAnalysisResult] = useState({ detected_skills: [], skill_count: 0 })
  const [analysisError, setAnalysisError] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [selectedStatus, setSelectedStatus] = useState('All')
  const [selectedApplicationId, setSelectedApplicationId] = useState(null)

  useEffect(() => {
    loadApplications()
  }, [])

  useEffect(() => {
    if (!successMessage) {
      return undefined
    }

    const timer = window.setTimeout(() => setSuccessMessage(''), 3000)
    return () => window.clearTimeout(timer)
  }, [successMessage])

  async function loadApplications() {
    setLoading(true)
    setError('')

    try {
      const data = await fetchApplications()
      setApplications(data)
    } catch (err) {
      setError(err.message || 'Unable to load applications.')
    } finally {
      setLoading(false)
    }
  }

  function resetForm() {
    setForm(initialForm)
    setFormErrors({})
    setIsEditing(false)
    setEditingId(null)
  }

  function validateForm() {
    const nextErrors = {}

    if (!form.company.trim()) {
      nextErrors.company = 'Company name is required.'
    }

    if (!form.role.trim()) {
      nextErrors.role = 'Role is required.'
    }

    if (form.job_description.length > 20000) {
      nextErrors.job_description = 'Job description must be 20,000 characters or fewer.'
    }

    return nextErrors
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextErrors = validateForm()
    setFormErrors(nextErrors)

    if (Object.keys(nextErrors).length > 0) {
      return
    }

    setSaving(true)
    setError('')

    try {
      const payload = {
        company: form.company.trim(),
        role: form.role.trim(),
        job_description: form.job_description.trim(),
        status: form.status,
      }

      const result = isEditing
        ? await updateApplication(editingId, payload)
        : await createApplication(payload)

      if (isEditing) {
        setApplications((current) =>
          current.map((application) =>
            application.id === result.id ? result : application,
          ),
        )
        setSuccessMessage('Application updated successfully.')
      } else {
        setApplications((current) => [result, ...current])
        setSuccessMessage('Application created successfully.')
      }

      resetForm()
    } catch (err) {
      setError(err.message || 'Unable to save application.')
    } finally {
      setSaving(false)
    }
  }

  function handleEdit(application) {
    setIsEditing(true)
    setEditingId(application.id)
    setForm({
      company: application.company,
      role: application.role,
      job_description: application.job_description,
      status: application.status,
    })
    setFormErrors({})
    setError('')
  }

  async function handleDelete(applicationId) {
    const confirmed = window.confirm('Delete this application?')
    if (!confirmed) {
      return
    }

    try {
      await deleteApplication(applicationId)
      setApplications((current) => current.filter((application) => application.id !== applicationId))
      setSuccessMessage('Application deleted successfully.')
      if (editingId === applicationId) {
        resetForm()
      }
    } catch (err) {
      setError(err.message || 'Unable to delete application.')
    }
  }

  async function handleAnalyze() {
    if (!analysisText.trim()) {
      setAnalysisResult({ detected_skills: [], skill_count: 0 })
      setAnalysisError('Paste a job description to analyze skills.')
      return
    }

    setAnalyzing(true)
    setAnalysisError('')

    try {
      const result = await analyzeDescription(analysisText)
      setAnalysisResult(result)
    } catch (err) {
      setAnalysisError(err.message || 'Skill analysis failed.')
      setAnalysisResult({ detected_skills: [], skill_count: 0 })
    } finally {
      setAnalyzing(false)
    }
  }

  const stats = useMemo(() => {
    return {
      total: applications.length,
      applied: applications.filter((application) => application.status === 'Applied').length,
      interviews: applications.filter((application) => application.status === 'Interview').length,
      offers: applications.filter((application) => application.status === 'Offer').length,
      rejections: applications.filter((application) => application.status === 'Rejected').length,
    }
  }, [applications])

  const filteredApplications = useMemo(() => {
    if (selectedStatus === 'All') {
      return applications
    }
    return applications.filter((application) => application.status === selectedStatus)
  }, [applications, selectedStatus])

  const selectedApplication = useMemo(
    () => applications.find((application) => application.id === selectedApplicationId) || null,
    [applications, selectedApplicationId],
  )

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-wrap">
          <div className="brand-mark">CP</div>
          <div>
            <p className="eyebrow">Student career tracker</p>
            <h1>CareerPilot</h1>
          </div>
        </div>

        <button type="button" className="primary-button" onClick={resetForm}>
          + Add application
        </button>
      </header>

      <main className="page">
        <section className="summary-grid" aria-label="Application statistics">
          <article className="stat-card">
            <span className="stat-label">Total</span>
            <strong>{stats.total}</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Applied</span>
            <strong>{stats.applied}</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Interviews</span>
            <strong>{stats.interviews}</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Offers</span>
            <strong>{stats.offers}</strong>
          </article>
          <article className="stat-card">
            <span className="stat-label">Rejections</span>
            <strong>{stats.rejections}</strong>
          </article>
        </section>

        <div className="content-grid">
          <section className="panel applications-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Applications</p>
                <h2>Saved roles</h2>
              </div>
              <button type="button" className="secondary-button" onClick={loadApplications}>
                Refresh
              </button>
            </div>

            {error && <p className="alert alert-error">{error}</p>}
            {successMessage && <p className="alert alert-success">{successMessage}</p>}

            <div className="status-filters" aria-label="Application filters">
              {['All', ...statusOptions].map((status) => (
                <button
                  key={status}
                  type="button"
                  className={selectedStatus === status ? 'filter-chip active' : 'filter-chip'}
                  onClick={() => setSelectedStatus(status)}
                >
                  {status}
                </button>
              ))}
            </div>

            {loading ? (
              <div className="empty-state">Loading applications...</div>
            ) : filteredApplications.length === 0 ? (
              <div className="empty-state">
                No applications match this status yet.
              </div>
            ) : (
              <div className="application-list">
                {filteredApplications.map((application) => (
                  <article className="application-card" key={application.id}>
                    <div className="application-main">
                      <div>
                        <h3>{application.company}</h3>
                        <p>{application.role}</p>
                      </div>
                      <span className="status-badge">{application.status}</span>
                    </div>

                    <p className="description-preview">
                      {application.job_description || 'No job description added yet.'}
                    </p>

                    <div className="application-meta">
                      <span>Created {new Date(application.created_at).toLocaleDateString()}</span>
                      <div className="action-row">
                        <button
                          type="button"
                          className="text-button"
                          onClick={() => setSelectedApplicationId(application.id)}
                        >
                          Details
                        </button>
                        <button type="button" className="text-button" onClick={() => handleEdit(application)}>
                          Edit
                        </button>
                        <button
                          type="button"
                          className="text-button danger"
                          onClick={() => handleDelete(application.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}

            {selectedApplication && (
              <div className="detail-card">
                <div className="detail-header">
                  <div>
                    <p className="eyebrow">Selected role</p>
                    <h3>{selectedApplication.company}</h3>
                  </div>
                  <button type="button" className="text-button" onClick={() => setSelectedApplicationId(null)}>
                    Close
                  </button>
                </div>

                <p className="detail-role">{selectedApplication.role}</p>
                <div className="detail-meta">
                  <span>Status: {selectedApplication.status}</span>
                  <span>Created: {new Date(selectedApplication.created_at).toLocaleDateString()}</span>
                </div>
                <p className="detail-description">
                  {selectedApplication.job_description || 'No job description has been saved for this application.'}
                </p>
              </div>
            )}
          </section>

          <aside className="panel side-panel">
            <div className="panel-header stacked">
              <div>
                <p className="eyebrow">Application details</p>
                <h2>{isEditing ? 'Edit application' : 'Add application'}</h2>
              </div>
            </div>

            <form className="application-form" onSubmit={handleSubmit}>
              <label>
                <span>Company</span>
                <input
                  type="text"
                  value={form.company}
                  onChange={(event) => setForm({ ...form, company: event.target.value })}
                  placeholder="Google"
                />
                {formErrors.company && <small>{formErrors.company}</small>}
              </label>

              <label>
                <span>Role</span>
                <input
                  type="text"
                  value={form.role}
                  onChange={(event) => setForm({ ...form, role: event.target.value })}
                  placeholder="Software Engineer Intern"
                />
                {formErrors.role && <small>{formErrors.role}</small>}
              </label>

              <label>
                <span>Status</span>
                <select
                  value={form.status}
                  onChange={(event) => setForm({ ...form, status: event.target.value })}
                >
                  {statusOptions.map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                <span>Job description</span>
                <textarea
                  rows="6"
                  value={form.job_description}
                  onChange={(event) => setForm({ ...form, job_description: event.target.value })}
                  placeholder="Paste the full job description here."
                />
                {formErrors.job_description && <small>{formErrors.job_description}</small>}
              </label>

              <div className="form-actions">
                <button type="submit" className="primary-button" disabled={saving}>
                  {saving ? 'Saving...' : isEditing ? 'Update application' : 'Save application'}
                </button>
                <button type="button" className="secondary-button" onClick={resetForm}>
                  Cancel
                </button>
              </div>
            </form>

            <div className="divider" />

            <div className="analysis-panel">
              <div className="panel-header stacked">
                <div>
                  <p className="eyebrow">Skill intelligence</p>
                  <h2>Job description analysis</h2>
                </div>
              </div>

              <textarea
                rows="6"
                value={analysisText}
                onChange={(event) => setAnalysisText(event.target.value)}
                placeholder="Paste a job description to detect relevant technical skills."
              />

              <div className="form-actions compact">
                <button type="button" className="primary-button" onClick={handleAnalyze} disabled={analyzing}>
                  {analyzing ? 'Analyzing...' : 'Analyze'}
                </button>
              </div>

              {analysisError && <p className="alert alert-error">{analysisError}</p>}

              {analysisResult.detected_skills.length > 0 ? (
                <>
                  <div className="skill-summary">
                    <strong>{analysisResult.skill_count}</strong>
                    <span>skills detected</span>
                  </div>
                  <div className="skill-tags">
                    {analysisResult.detected_skills.map((skill) => (
                      <span className="skill-tag" key={skill}>
                        {skill}
                      </span>
                    ))}
                  </div>
                </>
              ) : (
                <p className="muted">No known skills detected yet.</p>
              )}
            </div>
          </aside>
        </div>
      </main>
    </div>
  )
}

export default App
