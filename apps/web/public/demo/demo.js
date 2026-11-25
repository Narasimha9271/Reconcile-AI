"use strict";
// No network requests, production credentials, uploads, or persistent storage.
const el = id => document.getElementById(id);
let actor = null, maker = null, decision = null;
const mayDecide = () => Boolean(actor && maker && actor !== maker && !decision);
function render() {
  el("identity").textContent = actor ? "Demo login: " + actor + " · Finance approver" : "Not signed in to the demo.";
  el("submit").disabled = !actor || Boolean(maker);
  el("approve").disabled = el("reject").disabled = !mayDecide();
  el("status").textContent = !maker ? "No invoice submitted yet." : decision ? decision :
    "Review required: INR 250.00 above PO. Submitted by " + maker + ". " +
    (actor === maker ? "You cannot review your own submission. Switch test login to continue." : "You can approve or reject this exception.");
}
for (const name of ["Maya","Leo"]) el(name.toLowerCase()).onclick = () => { actor = name; render(); };
el("submit").onclick = () => { if (actor && !maker) maker = actor; render(); };
for (const action of ["approve","reject"]) el(action).onclick = () => {
  if (mayDecide()) decision = (action === "approve" ? "Approved" : "Rejected") + " by " + actor + " · Submitted by " + maker + ".";
  render();
};
el("reset").onclick = () => { actor = maker = decision = null; render(); };
render();
