import React from 'react';
import { Switch, Route } from 'react-router-dom';

// import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';
import ShopPage from './components/ShopPage';
import ShoppingCart from './components/ShoppingCart';

function App() {
  return (
    <Router>
      <div>
        <Navbar />
        <Switch>
          <Route exact path="/" component={HomePage} />
          <Route exact path="/shop" component={ShopPage} />
          <Route exact path="/cart" component={ShoppingCart} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;
