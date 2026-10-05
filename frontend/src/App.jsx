import { useState } from "react";
import LicensesPanel from "./components/LicensesPanel.jsx";
import ProductsPanel from "./components/ProductsPanel.jsx";
import UsersPanel from "./components/UsersPanel.jsx";
import ValidatePanel from "./components/ValidatePanel.jsx";

const TABS = [
  { id: "licenses", label: "Licenses", Component: LicensesPanel },
  { id: "validate", label: "Validate", Component: ValidatePanel },
  { id: "products", label: "Products", Component: ProductsPanel },
  { id: "users", label: "Users", Component: UsersPanel },
];

export default function App() {
  const [tab, setTab] = useState("licenses");
  const { Component } = TABS.find((t) => t.id === tab);

  return (
    <div className="app">
      <header>
        <h1>License Portal</h1>
        <nav role="tablist">
          {TABS.map((t) => (
            <button
              key={t.id}
              role="tab"
              aria-selected={tab === t.id}
              className={tab === t.id ? "tab active" : "tab"}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>
      <main>
        <Component />
      </main>
    </div>
  );
}
