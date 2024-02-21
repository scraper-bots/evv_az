import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ProductCard from './ProductCard';

test('renders product card with correct title and price', () => {
  const product = {
    title: 'Test Product',
    description: 'This is a test product',
    price: 10
  };
  render(<ProductCard product={product} />);
  
  expect(screen.getByText('Test Product')).toBeInTheDocument();
  expect(screen.getByText('$10')).toBeInTheDocument();
});

test('increments and decrements quantity correctly', () => {
  const product = {
    title: 'Test Product',
    description: 'This is a test product',
    price: 10
  };
  render(<ProductCard product={product} />);
  
  const incrementButton = screen.getByText('+');
  const decrementButton = screen.getByText('-');
  const quantityInput = screen.getByRole('textbox', { name: /quantity/i });

  fireEvent.click(incrementButton);
  expect(quantityInput.value).toBe('2');

  fireEvent.click(decrementButton);
  expect(quantityInput.value).toBe('1');
});
