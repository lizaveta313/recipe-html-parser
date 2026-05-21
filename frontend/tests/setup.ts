import "@testing-library/jest-dom/vitest";
import * as React from "react";

(globalThis as typeof globalThis & { React: typeof React }).React = React;
