/**
 * Public API surface for the frontend.
 * Implementation is split under ./ for easier navigation.
 */

export { api } from "./instance";
export {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
} from "./tasksApi";
export {
  getAvailability,
  createAvailability,
  updateAvailability,
  deleteAvailability,
} from "./availabilityApi";
export {
  getConstraints,
  createConstraint,
  updateConstraint,
  deleteConstraint,
} from "./constraintsApi";
export {
  getSchedule,
  generateSchedule,
  moveScheduleBlock,
  deleteScheduleBlock,
  exportSchedule,
} from "./scheduleApi";
