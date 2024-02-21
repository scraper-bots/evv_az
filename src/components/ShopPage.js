import React, { useState, useEffect } from 'react';

const ShopPage = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    // Fetch products from API
    fetch('https://fakestoreapi.com/products')
      .then(response => response.json())
      .then(data => setProducts(data));
  }, []);

  return (
    <div>
      <h1>Shop</h1>
      <ul>
        {products.map(product => (
          <li key={product.id}>{product.title}</li>
        ))}
      </ul>
    </div>
  );
}

export default ShopPage;
