/* global localStorage, fetch */

import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { BrowserRouter, Route, Switch, Redirect } from 'react-router-dom'

import UserPage from './User/UserPage'
import Login from './Login/Login'
import Error from './shared/Error'
import NavBar from './shared/Navigation'
import Register from './Login/Register'
import Shop from './Shop/Shop'
import AddShopForm from './User/AddShopForm.js'

import Container from '@material-ui/core/Container'

class App extends Component {
  constructor (props) {
    super(props)
    this.state = {
      logged_in: !!localStorage.getItem('token'),
      email: ''
    }
  }

  componentDidMount () {
    if (this.state.logged_in) {
      fetch('http://localhost:8000/api/current_user/', {
        headers: {
          Authorization: `Token ${localStorage.getItem('token')}`
        }
      })
        .then(res => res.json())
        .then(json => {
          this.setState({ email: json.email })
        })
    }
  }

  logOut (event) {
    localStorage.removeItem('token')
    this.setState({ logged_in: false, email: '' })
  }

  render () {
    const PrivateRoute = ({ ...props }) => this.state.logged_in ? <Route {...props} /> : <Redirect to='/login' />
    return (
      <BrowserRouter>
        <NavBar isLogged={this.state.logged_in} handleLogOut={(event) => this.logOut(event)} />

        <Container fixed>
          <Switch>
            <PrivateRoute path='/' component={UserPage} exact />
            <Route path='/login' component={Login} exact />
            <PrivateRoute path='/register' component={Register} exact />
            <PrivateRoute path='/register_shop' component={AddShopForm} exact />
            <PrivateRoute path='/shop/:shopID' component={Shop} exact />
            <Route component={Error} />
          </Switch>
        </Container>
      </BrowserRouter>
    )
  }
}

App.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired
  })
}

export default App
