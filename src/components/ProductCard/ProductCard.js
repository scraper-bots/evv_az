import React, { useState } from 'react';
import styles from './ProductCard.module.css';

const ProductCard = ({ product }) => {
  const [quantity, setQuantity] = useState(1);

  const handleIncrement = () => {
    setQuantity(prevQuantity => prevQuantity + 1);
  }

  const handleDecrement = () => {
    if (quantity > 1) {
      setQuantity(prevQuantity => prevQuantity - 1);
    }
  }

  const handleAddToCart = () => {
    // Implement logic to add product to cart
  }

  return (
    <div className={styles.card}>
      <h3>{product.title}</h3>
      <p>{product.description}</p>
      <p>${product.price}</p>
      <div className={styles.inputContainer}>
        <span>Quantity:</span>
        <input className={styles.inputField} type="number" value={quantity} onChange={e => setQuantity(e.target.value)} />
        <button className={styles.button} onClick={handleDecrement}>-</button>
        <button className={styles.button} onClick={handleIncrement}>+</button>
      </div>
      <button onClick={handleAddToCart}>Add to Cart</button>
    </div>
  );
}

export default ProductCard;
