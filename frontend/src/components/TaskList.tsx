/** Task list - create, view, delete tasks. */

import { useState, useEffect } from "react";
import { getTasks, createTask, deleteTask } from "../api/client";
import "./TaskList.css";
import type { Task, TaskCreate } from "../types/task";


const DEFAULT_FORM: TaskCreate = {
  name: "",
  estimated_duration_minutes: 30,
  priority: 0,
  splittable: false,
};


export default function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<TaskCreate>(DEFAULT_FORM);


  useEffect(function onMount() {
    loadTasks();
  }, []);



  async function loadTasks() {
    try {
      const res = await getTasks();
      setTasks(res.data);
    } catch {
      setTasks([]);
    } finally {
      setLoading(false);
    }
  }



  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.name.trim()) {
      return;
    }
    try {
      await createTask(formData);
      setFormData(DEFAULT_FORM);
      setShowForm(false);
      loadTasks();
    } catch (err) {
      console.error("Failed to create task:", err);
    }
  }



  async function handleDelete(id: number) {
    try {
      await deleteTask(id);
      loadTasks();
    } catch (err) {
      console.error("Failed to delete task:", err);
    }
  }



  function getSplittableSuffix(task: Task): string {
    if (task.splittable) {
      return " · Splittable";
    } else {
      return "";
    }
  }



  function handleToggleForm() {
    setShowForm(!showForm);
  }



  function handleNameChange(e: React.ChangeEvent<HTMLInputElement>) {
    setFormData({ ...formData, name: e.target.value });
  }



  function handleDurationChange(e: React.ChangeEvent<HTMLInputElement>) {
    const val = parseInt(e.target.value);
    let mins = 30;
    if (!isNaN(val)) {
      mins = val;
    }
    setFormData({
      ...formData,
      estimated_duration_minutes: mins,
    });
  }



  function handleSplittableChange(e: React.ChangeEvent<HTMLInputElement>) {
    setFormData({ ...formData, splittable: e.target.checked });
  }



  function getAddButtonLabel(): string {
    if (showForm) {
      return "Cancel";
    } else {
      return "+ Add Task";
    }
  }



  function renderTaskItem(task: Task) {
    function onDeleteClick() {
      handleDelete(task.id);
    }
    return (
      <li key={task.id} className="task-item">
        <div>
          <strong>{task.name}</strong>
          <span className="task-meta">
            {task.estimated_duration_minutes} min · Priority {task.priority}
            {getSplittableSuffix(task)}
          </span>
        </div>
        <button
          className="btn-danger"
          onClick={onDeleteClick}
          aria-label="Delete task"
        >
          Delete
        </button>
      </li>
    );
  }



  function getTaskListContent() {
    if (tasks.length === 0 && !showForm) {
      return (
        <li className="task-empty">No tasks yet. Add one to get started.</li>
      );
    } else {
      const items = [];
      for (let i = 0; i < tasks.length; i++) {
        items.push(renderTaskItem(tasks[i]));
      }
      return items;
    }
  }



  if (loading) {
    return <div className="task-list">Loading tasks...</div>;
  }

  return (
    <div className="task-list">
      <div className="task-list-header">
        <h2>Tasks</h2>
        <button className="btn-primary" onClick={handleToggleForm}>
          {getAddButtonLabel()}
        </button>
      </div>

      {showForm && (
        <form className="task-form" onSubmit={handleCreate}>
          <input
            type="text"
            placeholder="Task name"
            value={formData.name}
            onChange={handleNameChange}
            required
          />
          <input
            type="number"
            min={1}
            placeholder="Duration (min)"
            value={formData.estimated_duration_minutes}
            onChange={handleDurationChange}
          />
          <label>
            <input
              type="checkbox"
              checked={formData.splittable}
              onChange={handleSplittableChange}
            />
            Splittable
          </label>
          <button type="submit">Create</button>
        </form>
      )}

      <ul className="task-items">
        {getTaskListContent()}
      </ul>
    </div>
  );
}
