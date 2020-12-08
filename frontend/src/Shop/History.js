/* global localStorage */
/* istanbul ignore file */
/* eslint react/prop-types: 0 */

import React from 'react'
import Typography from '@material-ui/core/Typography'
import axios from 'axios'
import Box from '@material-ui/core/Box'
import { DataGrid } from '@material-ui/data-grid'

class History extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      storeName: '',
      items: []
    }
  }

  componentDidMount () {
    const storeID = this.props.match.params.shopID
    axios.get('http://127.0.0.1:8000/api/stores/' + storeID, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then((res) => {
        this.setState({ storeName: res.data.name, items: res.data.items })
        console.log(this.state)
      })
      .catch((error) => {
        console.error(error)
      })
  }

  render () {
    const columns = [
      { field: 'col1', headerName: 'Date/Time', width: 250 },
      { field: 'col2', headerName: 'Action', width: 150 },
      { field: 'col3', headerName: 'Item Name', width: 150 },
      { field: 'col4', headerName: 'After Price', width: 150 },
      { field: 'col5', headerName: 'After Stock', width: 150 },
      { field: 'col6', headerName: 'After Description', width: 300 }
    ]

    const rows = []

    for (const key in this.state.items) {
      const hist = this.state.items[key]
      const name = hist.name
      const his = hist.history
      let obj
      for (let i = 0; i < his.length; i++) {
        obj = his[i]
        const idd = rows.length + 1
        const d = new Date(obj.datetime)
        const arr = { id: idd, col1: d.toLocaleString('en-US', { timeZone: 'America/New_York' }), col2: obj.category, col3: name, col4: obj.after_price, col5: obj.after_stock, col6: obj.after_description }
        rows.push(arr)
      }
    }

    return (
      <div>
        <Box mb={4} mt={2}>
          <Typography component='h1' variant='h5'>
            Item History for Your Store: {this.state.storeName}
          </Typography>
        </Box>
        <Box style={{ height: 600, width: '100%' }}>
          <DataGrid sortingOrder={['desc', 'asc', null]} rows={rows} columns={columns} />
        </Box>
      </div>
    )
  }
}

export default History
