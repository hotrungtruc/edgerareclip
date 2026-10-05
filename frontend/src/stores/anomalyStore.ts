import { create } from "zustand";

export const useAnomalyStore = create(() => ({ anomalies: [] }));
