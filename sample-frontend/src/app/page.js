"use client";

import { useState } from "react";
import GovBar from "@/components/layout/GovBar";
import Nav from "@/components/layout/Nav";
import LandingPage from "@/components/sections/LandingPage";
import SubmitPage from "@/components/sections/SubmitPage";
import ProcessingPage from "@/components/sections/ProcessingPage";
import DashboardPage from "@/components/sections/DashboardPage";
import FindingsPage from "@/components/sections/FindingsPage";
import QueuePage from "@/components/sections/QueuePage";
import ReportPage from "@/components/sections/ReportPage";
import DirectoryPage from "@/components/sections/DirectoryPage";
import { THEME } from "@/lib/api";

export default function App() {
  const [page, setPage] = useState("landing");

  const pages = {
    landing: <LandingPage go={setPage} />,
    submit: <SubmitPage go={setPage} />,
    processing: <ProcessingPage go={setPage} />,
    dashboard: <DashboardPage go={setPage} />,
    findings: <FindingsPage go={setPage} />,
    queue: <QueuePage go={setPage} />,
    report: <ReportPage go={setPage} />,
    directory: <DirectoryPage go={setPage} />,
  };

  return (
    <div style={{ fontFamily: "'Segoe UI',system-ui,-apple-system,sans-serif", lineHeight: 1.5, color: THEME.TX, minHeight: "100vh" }}>
      <GovBar />
      <Nav go={setPage} page={page} />
      {pages[page] || pages.landing}
    </div>
  );
}
