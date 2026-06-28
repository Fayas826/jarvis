import React from "react";
import { AppStateProvider } from "@/core/AppStateProvider";
import MainLayout from "@/layout/MainLayout";


export default function App() {
  return (
    <AppStateProvider>
      <MainLayout />
    </AppStateProvider>
  );
}
