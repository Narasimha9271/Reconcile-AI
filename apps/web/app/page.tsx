"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import "./styles.css";
import "./auth.css";

const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const AUTH = process.env.NEXT_PUBLIC_AUTH_BASE_URL ?? "http://localhost:4000";
type Vendor = { id: string; name: string };
type PurchaseOrder = { id: string; number: string };
type Reconciliation = { id: string; invoiceNumber: string; invoiceAmount: string; vendorName: string; matchStatus: string; confidence: number; explanation: string; decision?: string };
type CurrentUser = { name?: string | null; email?: string | null; role: string };

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { ...init, credentials: "include", headers: { ...(init?.headers ?? {}) } });
  if (!response.ok) throw new Error((await response.json()).detail ?? "Request failed");
  return response.json();
}

export default function Home() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([]);
  const [cases, setCases] = useState<Reconciliation[]>([]);
  const [ready, setReady] = useState(false);
  const [notice, setNotice] = useState("Loading workspace...");
  const [busy, setBusy] = useState(false);

  const refresh = async () => {
    try {
      const [me, loadedVendors, loadedPOs, loadedCases] = await Promise.all([api<CurrentUser>("/v1/me"), api<Vendor[]>("/v1/vendors"), api<PurchaseOrder[]>("/v1/purchase-orders"), api<Reconciliation[]>("/v1/reconciliations")]);
      setUser(me); setVendors(loadedVendors); setPurchaseOrders(loadedPOs); setCases(loadedCases); setNotice("Workspace is up to date.");
    } catch (error) { setUser(null); setNotice((error as Error).message); }
    finally { setReady(true); }
  };
  useEffect(() => { refresh(); }, []);
  const openCases = cases.filter((item) => !item.decision);
  const totals = useMemo(() => ({ open: openCases.length, exceptions: openCases.filter((item) => item.matchStatus === "EXCEPTION").length, matched: cases.filter((item) => item.matchStatus === "MATCHED").length }), [cases]);

  async function submit(path: string, body: object, form?: HTMLFormElement) {
    setBusy(true);
    try { await api(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); form?.reset(); await refresh(); }
    catch (error) { setNotice((error as Error).message); } finally { setBusy(false); }
  }
  async function createVendor(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const form = new FormData(event.currentTarget); await submit("/v1/vendors", { name: form.get("name"), external_ref: form.get("reference") || null }, event.currentTarget); }
  async function createPO(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const form = new FormData(event.currentTarget); await submit("/v1/purchase-orders", { vendor_id: form.get("vendor"), number: form.get("number"), currency: "USD", lines: [{ line_no: 1, description: form.get("description"), quantity: form.get("quantity"), unit_price: form.get("unitPrice") }] }, event.currentTarget); }
  async function createCase(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const form = new FormData(event.currentTarget); await submit("/v1/reconciliations", { purchase_order_id: form.get("po"), invoice_number: form.get("invoice"), invoice_amount: form.get("amount"), currency: "USD", vendor_name: form.get("vendorName") }, event.currentTarget); }
  async function decide(id: string, decision: "APPROVED" | "REJECTED") { await submit(`/v1/reconciliations/${id}/decision`, { decision }); }
  async function logout() { await fetch(`${AUTH}/api/auth/google/logout`, { method: "POST", credentials: "include" }); setUser(null); setVendors([]); setPurchaseOrders([]); setCases([]); setReady(true); }

  if (!ready) return <main className="authPage"><div className="loginCard"><p className="eyebrow">RECONCILEAI</p><h2>Loading secure workspace...</h2></div></main>;
  if (!user) return <LoginScreen authUrl={`${AUTH}/api/auth/google/login`} />;
  return <main>
    <aside><div className="brand"><span>R</span> ReconcileAI</div><nav><a className="active" href="#overview">Overview</a><a href="#workspace">Procurement</a><a href="#queue">Review queue</a></nav><div className="identity"><b>{user.name ?? "Workspace member"}</b><small>{user.email ?? user.role}</small></div></aside>
    <section className="shell"><header><div><p className="eyebrow">FINANCE OPERATIONS</p><h1>Reconciliation workspace</h1><p className="muted">Turn invoice checks into a fast, auditable decision.</p></div><div className="userControls"><div><b>{user.name ?? "Workspace member"}</b><small>{user.email}</small></div><button className="secondary" onClick={refresh}>Refresh data</button><button className="logout" onClick={logout}>Log out</button></div></header>
      <p className="notice">{notice}</p><div className="metrics" id="overview"><Metric label="Open decisions" value={totals.open} /><Metric label="Exceptions" value={totals.exceptions} tone="danger" /><Metric label="Auto matches" value={totals.matched} tone="good" /></div>
      <section className="workspace" id="workspace"><Panel title="1. Create vendor"><form onSubmit={createVendor}><input name="name" placeholder="Vendor name" required /><input name="reference" placeholder="External reference (optional)" /><button disabled={busy}>Add vendor</button></form><div className="chips">{vendors.map((vendor) => <span key={vendor.id}>{vendor.name}</span>)}</div></Panel><Panel title="2. Create purchase order"><form onSubmit={createPO}><select name="vendor" required defaultValue=""><option value="" disabled>Select vendor</option>{vendors.map((vendor) => <option key={vendor.id} value={vendor.id}>{vendor.name}</option>)}</select><input name="number" placeholder="PO number, e.g. PO-1001" required /><input name="description" placeholder="Line description" required /><div className="two"><input name="quantity" type="number" step="0.01" min="0.01" placeholder="Quantity" required /><input name="unitPrice" type="number" step="0.01" min="0" placeholder="Unit price" required /></div><button disabled={busy || !vendors.length}>Create PO</button></form></Panel><Panel title="3. Reconcile invoice"><form onSubmit={createCase}><select name="po" required defaultValue=""><option value="" disabled>Select purchase order</option>{purchaseOrders.map((po) => <option key={po.id} value={po.id}>{po.number}</option>)}</select><input name="invoice" placeholder="Invoice number" required /><input name="vendorName" placeholder="Invoice vendor name" required /><input name="amount" type="number" step="0.01" min="0" placeholder="Invoice amount" required /><button disabled={busy || !purchaseOrders.length}>Run reconciliation</button></form></Panel></section>
      <section className="queue" id="queue"><div className="queue-heading"><div><p className="eyebrow">HUMAN-IN-THE-LOOP</p><h2>Review queue</h2></div><span>{openCases.length} awaiting decision</span></div>{cases.length === 0 ? <div className="empty">Create a vendor, PO, and invoice above to start the workflow.</div> : <div className="case-list">{cases.map((item) => <article key={item.id} className="case"><div><div className="case-title"><b>{item.invoiceNumber}</b><Status value={item.matchStatus} /></div><p>{item.vendorName} · ${item.invoiceAmount} · Confidence {Math.round(item.confidence * 100)}%</p><small>{item.explanation}</small></div>{item.decision ? <span className="decision">{item.decision}</span> : <div className="actions"><button className="approve" disabled={busy} onClick={() => decide(item.id, "APPROVED")}>Approve</button><button className="reject" disabled={busy} onClick={() => decide(item.id, "REJECTED")}>Reject</button></div>}</article>)}</div>}</section>
    </section>
  </main>;
}

function LoginScreen({ authUrl }: { authUrl: string }) { return <main className="authPage"><section className="authHero"><div className="authBrand"><span>R</span> ReconcileAI</div><p className="eyebrow">FINANCE OPERATIONS, SIMPLIFIED</p><h1>Every invoice. Matched with confidence.</h1><p>Transform scattered invoices, purchase orders, and vendor quotes into fast, auditable decisions.</p><div className="authBenefits"><span>✓ Explainable matching</span><span>✓ Human approval controls</span><span>✓ Tenant-secure workspace</span></div></section><section className="authPanel"><div className="loginCard"><p className="eyebrow">WELCOME TO RECONCILEAI</p><h2>Sign in to your workspace</h2><p>Use your approved Google account to continue. New approved users are set up automatically.</p><a className="googleButton" href={authUrl}><b>G</b> Continue with Google</a><small>Access is limited to approved organization emails.</small></div></section></main>; }
function Panel({ title, children }: { title: string; children: React.ReactNode }) { return <div className="panel"><h2>{title}</h2>{children}</div>; }
function Metric({ label, value, tone = "" }: { label: string; value: number; tone?: string }) { return <div className={`metric ${tone}`}><span>{label}</span><strong>{value}</strong></div>; }
function Status({ value }: { value: string }) { return <span className={`status ${value.toLowerCase()}`}>{value.replaceAll("_", " ")}</span>; }
