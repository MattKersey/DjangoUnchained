/* global localStorage, fetch */

import React from 'react'
import Box from '@material-ui/core/Box'
import Table from '@material-ui/core/Table'
import TableBody from '@material-ui/core/TableBody'
import TableCell from '@material-ui/core/TableCell'
import TableContainer from '@material-ui/core/TableContainer'
import TableHead from '@material-ui/core/TableHead'
import TableRow from '@material-ui/core/TableRow'
import Button from '@material-ui/core/Button'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'

class ShopHistory extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      history: []
    }
  }

  componentDidMount () {
    const storeID = this.props.match.params.shopID
    fetch('http://127.0.0.1:8000/api/stores/' + storeID + '/', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(res => res.json())
      .then(json => {
        let history = []
        for (let i = 0; i < json.items.length; i++) {
          console.log(json.items[i].history)
          history = history.concat(json.items[i].history)
        }
        history.sort(function (a, b) { return parseFloat(a.datetime) - parseFloat(b.datetime) })
        const historyElements = []
        for (let i = 0; i < history.length; i++) {
          const historyRow = (
            <TableRow>
              <TableCell>{history[i].category}</TableCell>
              <TableCell>{history[i].before_stock}</TableCell>
              <TableCell>{history[i].after_stock}</TableCell>
            </TableRow>
          )
          historyElements.push(historyRow)
        }
        this.setState({ history: historyElements, store_id: storeID })
        console.log(this.state)
      })
  }

  render () {
    return (
      <div align='center'>
        <Typography component='h1' variant='h5'>
          Store History:
        </Typography>
        <TableContainer component={Paper}>
          <Table aria-label='simple table'>
            <TableBody>
              {this.state.history}
            </TableBody>
          </Table>
        </TableContainer>
      </div>
    )
  }
}

export default ShopHistory
