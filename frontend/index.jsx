import React, { useState, useEffect } from 'react';

const API_BASE = "http://localhost:8000/api/v1";

export default function AltCreditDashboard() {
  const [personas, setPersonas] = useState([]);
  const [selectedPersona, setSelectedPersona] = useState("Priya");
  const [telemetry, setTelemetry] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [uploadError, setUploadError] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/personas`)
      .then((res) => res.json())
      .then((data) => setPersonas(data))
      .catch((err) => console.error("Error loading personas:", err));
    fetchTelemetry("Priya");
  }, []);

  const fetchTelemetry = async (persona) => {
    setLoading(true);
    setUploadError(null);
    try {
      const res = await fetch(`${API_BASE}/ingest/simulate-aa?persona=${persona}`, {
        method: 'POST'
      });
      if (!res.ok) throw new Error("Failed to load persona data");
      const data = await res.json();
      setTelemetry(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/ingest/upload`, {
        method: 'POST',
        body: formData
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Upload failed");
      }
      const data = await res.json();
      setTelemetry(data);
      setSelectedPersona("");
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredTransactions = (telemetry?.sanitized_transactions || []).filter((t) => {
    const q = searchFilter.toLowerCase();
    return (
      t.narration_clean?.toLowerCase().includes(q) ||
      t.category?.toLowerCase().includes(q) ||
      t.date?.includes(q)
    );
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10 font-sans">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-6 mb-8 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 uppercase tracking-wider">
              BNP Paribas Innoversité
            </span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800 uppercase tracking-wider">
              UC 3 • Slice 1
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold mt-2 text-white tracking-tight">
            AltCredit Telemetry & Ingestion Console
          </h1>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedPersona}
            onChange={(e) => {
              setSelectedPersona(e.target.value);
              fetchTelemetry(e.target.value);
            }}
            className="bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          >
            {personas.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>

          <label className="cursor-pointer bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm px-4 py-2 rounded-md transition shadow-sm">
            Upload Statement (CSV/JSON)
            <input
              type="file"
              onChange={handleFileUpload}
              className="hidden"
              accept=".csv,.json"
            />
          </label>
        </div>
      </div>

      {uploadError && (
        <div className="mb-6 p-4 rounded-md bg-rose-950/70 border border-rose-700 text-rose-300 text-sm">
          <strong>Error:</strong> {uploadError}
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-24 space-y-3">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-slate-400">Processing Account Aggregator records & sanitizing PII...</p>
        </div>
      ) : telemetry ? (
        <div className="space-y-6">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cash Inflow / Outflow</span>
              <p className="text-2xl font-bold mt-2 text-emerald-400">₹{telemetry.total_inflow.toLocaleString()}</p>
              <p className="text-xs text-rose-400 mt-1">Debit: -₹{telemetry.total_outflow.toLocaleString()}</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Daily Balance (ADB)</span>
              <p className="text-2xl font-bold mt-2 text-white">₹{telemetry.average_daily_balance.toLocaleString()}</p>
              <p className="text-xs text-slate-400 mt-1">Savings Rate: {telemetry.savings_rate_pct}%</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Liquidity Runway</span>
              <p className={`text-2xl font-bold mt-2 ${telemetry.liquidity_buffer_days < 10 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {telemetry.liquidity_buffer_days} Days
              </p>
              <p className="text-xs text-slate-400 mt-1">Discretionary Ratio: {(telemetry.discretionary_spend_ratio * 100).toFixed(0)}%</p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Anonymized Customer ID</span>
              <p className="text-2xl font-bold mt-2 font-mono text-cyan-400">{telemetry.sanitized_id}</p>
              <p className="text-xs text-emerald-400 mt-1">Consent Verified (AA)</p>
            </div>
          </div>

          {/* Underwriting Triggers / Risk Flags */}
          {telemetry.risk_flags.length > 0 ? (
            <div className="bg-rose-950/40 border border-rose-800/60 p-4 rounded-lg">
              <h3 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-2">
                Underwriting Risk Triggers Detected ({telemetry.risk_flags.length})
              </h3>
              <ul className="list-disc list-inside text-sm text-rose-200 space-y-1">
                {telemetry.risk_flags.map((flag, idx) => (
                  <li key={idx}>{flag}</li>
                ))}
              </ul>
            </div>
          ) : (
            <div className="bg-emerald-950/30 border border-emerald-800/50 p-4 rounded-lg text-emerald-300 text-sm flex items-center gap-2">
              <span className="text-base">✓</span> Zero active risk flags. Healthy baseline liquidity and recurring obligations maintained.
            </div>
          )}

          {/* Monthly Breakdown & Categorization Row */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Monthly Trend Mini-Table */}
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg lg:col-span-2">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-3">Monthly Cash Aggregation</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase">
                    <tr>
                      <th className="py-2 px-3">Month</th>
                      <th className="py-2 px-3 text-right">Inflow</th>
                      <th className="py-2 px-3 text-right">Outflow</th>
                      <th className="py-2 px-3 text-right">Net Savings</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {telemetry.monthly_trends.map((m) => (
                      <tr key={m.month}>
                        <td className="py-2 px-3 font-mono font-medium">{m.month}</td>
                        <td className="py-2 px-3 text-right text-emerald-400">₹{m.inflow.toLocaleString()}</td>
                        <td className="py-2 px-3 text-right text-rose-400">₹{m.outflow.toLocaleString()}</td>
                        <td className={`py-2 px-3 text-right font-medium ${m.net >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
                          {m.net >= 0 ? '+' : ''}₹{m.net.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Categorized Spend List */}
            <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-3">Spend Footprint</h3>
              <div className="space-y-2">
                {Object.entries(telemetry.categorized_spend).length === 0 ? (
                  <p className="text-xs text-slate-500">No debit categories identified.</p>
                ) : (
                  Object.entries(telemetry.categorized_spend).map(([cat, amt]) => (
                    <div key={cat} className="flex justify-between items-center text-xs border-b border-slate-800/60 pb-1.5">
                      <span className="text-slate-400 font-mono">{cat}</span>
                      <span className="text-slate-200 font-semibold">₹{amt.toLocaleString()}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Sanitized Transaction Ledger */}
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
                Sanitized Transaction Feed (PII Redacted)
              </h3>
              <input
                type="text"
                placeholder="Search masked text or category..."
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-xs px-3 py-1.5 rounded-md focus:outline-none focus:ring-1 focus:ring-emerald-500 w-full sm:w-64"
              />
            </div>

            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-950 text-slate-400 uppercase sticky top-0">
                  <tr>
                    <th className="py-2.5 px-3">Date</th>
                    <th className="py-2.5 px-3">Sanitized Narration</th>
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3 text-right">Amount</th>
                    <th className="py-2.5 px-3 text-right">Balance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {filteredTransactions.map((t) => (
                    <tr key={t.txn_id} className="hover:bg-slate-800/40">
                      <td className="py-2.5 px-3 font-mono text-slate-400">{t.date}</td>
                      <td className="py-2.5 px-3 font-medium text-slate-200">{t.narration_clean}</td>
                      <td className="py-2.5 px-3">
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                          {t.category}
                        </span>
                      </td>
                      <td className={`py-2.5 px-3 text-right font-semibold ${t.type === 'CREDIT' ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {t.type === 'CREDIT' ? '+' : '-'}₹{t.amount.toLocaleString()}
                      </td>
                      <td className="py-2.5 px-3 text-right text-slate-400 font-mono">
                        ₹{t.balance.toLocaleString()}
                      </td>
                    </tr>
                  ))}
                  {filteredTransactions.length === 0 && (
                    <tr>
                      <td colSpan="5" className="text-center py-6 text-slate-500">
                        No transactions found matching filter.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}