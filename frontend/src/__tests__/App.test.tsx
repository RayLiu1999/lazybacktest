import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('App Component', () => {
  it('renders the main application with title', () => {
    render(<App />);
    expect(screen.getByText(/LazyBacktest/i)).toBeInTheDocument();
    expect(screen.getByText(/Phase 7 UI/i)).toBeInTheDocument();
  });

  it('shows settings form in sidebar', () => {
    render(<App />);
    expect(screen.getByText(/股票交易策略回測工具/i)).toBeInTheDocument();
  });
});
