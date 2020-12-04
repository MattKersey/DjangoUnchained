/* global localStorage, fetch, Headers */
/* istanbul ignore file */
/* eslint react/prop-types: 0 */

import React from 'react'
import axios from 'axios'
import { DataGrid } from '@material-ui/data-grid'

class History extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      storeName: '',
      itemHistory: []
    }
  }

  componentDidMount () {
    const storeID = this.props.match.params.shopID
    /*
    const search = window.location.search
    const params = new URLSearchParams(search)
    const sessionID = params.get('session_id')
    const myHeaders = new Headers()
    myHeaders.append('Authorization', 'Bearer ' + localStorage.getItem('token'))
    myHeaders.append('Content-Type', 'application/json')
    const raw = JSON.stringify({ session_id: sessionID })
    const requestOptions = {
      method: 'GET',
      headers: myHeaders,
      body: raw,
      redirect: 'follow'
    }
*/
    axios.get('http://127.0.0.1:8000/api/stores/' + storeID, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then((res) => {
        this.setState({ storeName: res.data.name, itemHistory: res.data.items })
        console.log(this.state)
      })
      .catch((error) => {
        console.error(error)
      })

    /*
    fetch('http://127.0.0.1:8000/api/stores/' + storeID, requestOptions)
      .then(function (response) {
        return response.json()
      })
      .then(function (result) {
        window.location = '/shop/' + storeID + '/'
      })
      .then(function (result) {
        // If `redirectToCheckout` fails due to a browser or network
        // error, you should display the localized error message to your
        // customer using `error.message`.
        if (result.error) {
          console.log(result.error.message)
        }
      })
      .catch(function (error) {
        console.error('Error:', error)
      })
      */
  }

  render () {
    return (
      <div />
    )
  }
}

export default History
