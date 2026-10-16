import { Analytics } from "@vercel/analytics/react";
import mixpanel from "mixpanel-browser";

mixpanel.init("civicgpt-token", { api_host: "https://api-js.mixpanel.com" });

export default function Layout({ children }) {
  return (<html><head><link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet" /></head>
    <body>{children}<Analytics /></body></html>);
}
