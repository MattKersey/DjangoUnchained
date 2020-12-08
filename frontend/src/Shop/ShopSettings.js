/* global localStorage, alert, fetch, Headers */
/* istanbul ignore file */
/* eslint react/prop-types: 0 */

import React from 'react'
import Table from '@material-ui/core/Table'
import TableBody from '@material-ui/core/TableBody'
import TableCell from '@material-ui/core/TableCell'
import TableContainer from '@material-ui/core/TableContainer'
import TableHead from '@material-ui/core/TableHead'
import TableRow from '@material-ui/core/TableRow'
import Paper from '@material-ui/core/Paper'
import Select from '@material-ui/core/Select'
import MenuItem from '@material-ui/core/MenuItem'
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button'
import Box from '@material-ui/core/Box'

class ShopSettings extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      users: {},
      storeID: -1,
      username: '',
      role: 'Manager'
    }
    this.handleChange = this.handleChange.bind(this)
  }

  componentDidMount () {
    const storeID = this.props.match.params.shopID
    fetch('http://127.0.0.1:8000/api/stores/' + storeID + '/get_associations', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(res => res.json())
      .then(json => {
        const userHash = {}
        for (let i = 0; i < json.length; i++) {
          userHash[json[i].user_email] = json[i]
        }
        this.setState({ users: userHash, storeID: storeID })
      })
  }

  handleRoleChange (event, user) {
    const email = user.user_email
    const newUser = { ...user, role: event.target.value }
    const oldUsers = this.state.users
    oldUsers[email] = newUser
    this.setState({ oldUsers })

    const myHeaders = new Headers()
    myHeaders.append('Authorization', 'Bearer ' + localStorage.getItem('token'))
    myHeaders.append('Content-Type', 'application/x-www-form-urlencoded')
    myHeaders.append('Cookie', 'csrftoken=fwv3jTStrI5oyvMGcQMBNdlyN6YTKdsfCMTqHYp7gC2JxrAIHAEBhF0BYWXWhmBb')

    const urlencoded = new URLSearchParams()
    urlencoded.append('store_id', this.state.storeID)
    urlencoded.append('role', event.target.value)
    urlencoded.append('email', email)

    const requestOptions = {
      method: 'POST',
      headers: myHeaders,
      body: urlencoded,
      redirect: 'follow'
    }

    fetch('http://127.0.0.1:8000/api/users/change_role/', requestOptions)
      .then(response => response.text())
      .then(result => console.log(result))
      .catch(error => alert(error))
  }

  handleChange (event) {
    this.setState({ [event.target.name]: event.target.value })
  }

  handleAddMember () {
    const myHeaders = new Headers()
    myHeaders.append('Authorization', 'Bearer ' + localStorage.getItem('token'))
    myHeaders.append('Content-Type', 'application/x-www-form-urlencoded')
    myHeaders.append('Cookie', 'csrftoken=fwv3jTStrI5oyvMGcQMBNdlyN6YTKdsfCMTqHYp7gC2JxrAIHAEBhF0BYWXWhmBb')

    const urlencoded = new URLSearchParams()
    urlencoded.append('store_id', this.state.storeID)
    urlencoded.append('role', this.state.role)
    urlencoded.append('email', this.state.username)

    const requestOptions = {
      method: 'POST',
      headers: myHeaders,
      body: urlencoded,
      redirect: 'follow'
    }

    fetch('http://127.0.0.1:8000/api/users/change_role/', requestOptions)
      .then(response => response.text())
      .then(result => console.log(result))
      .catch(error => console.log('error', error))
    this.setState({ username: '', role: 'Manager' })
    window.location.reload()
  }

  render () {
    return (
      <div>
        <TableContainer component={Paper}>
          <Table aria-label='simple table'>
            <TableHead>
              <TableRow>
                <TableCell>User Email</TableCell>
                <TableCell>Role</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.keys(this.state.users).map((user) =>
                <TableRow key={this.state.users[user].user_email}>
                  <TableCell component='th' scope='row'>
                    {this.state.users[user].user_email}
                  </TableCell>
                  <TableCell component='th' scope='row'>
                    <Select onChange={(event) => this.handleRoleChange(event, this.state.users[user])} value={this.state.users[user].role}>
                      <MenuItem value='Manager'>Manager</MenuItem>
                      <MenuItem value='Vendor'>Vendor</MenuItem>
                      <MenuItem value='Employee'>Employee</MenuItem>
                    </Select>
                  </TableCell>
                </TableRow>
              )}
              <TableRow>
                <TableCell align='left' component='th' scope='row'>
                  <Box display='inline' mr={2}>Add</Box>
                  <TextField onChange={this.handleChange} value={this.state.username} name='username' />
                  <Box display='inline' ml={2} mr={2}>as a</Box>
                  <Select onChange={this.handleChange} value={this.state.role} name='role' labelId='Role'>
                    <MenuItem value='Manager'>Manager</MenuItem>
                    <MenuItem value='Vendor'>Vendor</MenuItem>
                    <MenuItem value='Employee'>Employee</MenuItem>
                  </Select>
                  <Box onClick={this.handleAddMember.bind(this)} display='inline' ml={2} mr={2}>
                    <Button variant='contained' color='primary'>
                      Add Member
                    </Button>
                  </Box>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </div>
    )
  }
}

export default ShopSettings
