/** DOM helpers for app bootstrap. */

export function getRootElement(): HTMLElement {
  const element = document.getElementById("root");
  if (element === null) {
    throw new Error("Could not find #root element to mount the app.");
  }
  return element;
}
