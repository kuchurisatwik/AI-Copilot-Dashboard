"use client";

import React from "react";
import Sidebar from "@/components/layout/Sidebar";

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-primary)" }}>
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <main
        style={{
          flex: 1,
          marginLeft: "var(--sidebar-width)",
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          transition: "margin-left var(--transition-normal)",
        }}
      >
        {/* Top Header Bar */}
        <header
          style={{
            height: "64px",
            borderBottom: "1px solid var(--border-primary)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 1.5rem",
            background: "var(--bg-secondary)",
            position: "sticky",
            top: 0,
            zIndex: 40,
          }}
        >
          {/* Risk Status Bar — always visible */}
          <div style={{ display: "flex", gap: "1.5rem", alignItems: "center" }}>
            <RiskIndicator label="Risk Exposure" value="0.0%" status="safe" />
            <RiskIndicator label="Daily Loss" value="0.0%" status="safe" />
            <RiskIndicator label="Drawdown" value="0.0%" status="safe" />
          </div>

          {/* Right side */}
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            {/* Notification bell */}
            <button
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--border-primary)",
                background: "transparent",
                color: "var(--text-secondary)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
                position: "relative",
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
                <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
              </svg>
            </button>

            {/* User avatar */}
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                background: "linear-gradient(135deg, var(--accent-primary), #8b5cf6)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "0.8125rem",
                fontWeight: 700,
                color: "white",
                cursor: "pointer",
              }}
            >
              TC
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div
          style={{
            flex: 1,
            padding: "1.5rem",
            overflow: "auto",
          }}
        >
          {children}
        </div>
      </main>
    </div>
  );
}

// ── Risk Indicator Component ──
function RiskIndicator({
  label,
  value,
  status,
}: {
  label: string;
  value: string;
  status: "safe" | "warning" | "danger";
}) {
  const colors = {
    safe: "var(--color-success)",
    warning: "var(--color-warning)",
    danger: "var(--color-danger)",
  };

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
      <div
        style={{
          width: "6px",
          height: "6px",
          borderRadius: "50%",
          background: colors[status],
          boxShadow: `0 0 6px ${colors[status]}`,
        }}
      />
      <div>
        <div
          style={{
            fontSize: "0.625rem",
            fontWeight: 500,
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            color: "var(--text-muted)",
            lineHeight: 1,
          }}
        >
          {label}
        </div>
        <div
          style={{
            fontSize: "0.8125rem",
            fontWeight: 700,
            color: colors[status],
            fontVariantNumeric: "tabular-nums",
            lineHeight: 1.3,
          }}
        >
          {value}
        </div>
      </div>
    </div>
  );
}
