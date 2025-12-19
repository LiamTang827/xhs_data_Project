#!/usr/bin/env node
// Simple check script to verify Mongo collection contents used by frontend API
// Usage: MONGO_URI="your_uri" node scripts/check_mongo.js

const { MongoClient } = require('mongodb')

async function main() {
  const uri = process.env.MONGO_URI
  if (!uri) {
    console.error('MONGO_URI not set. Set it in env before running:')
    console.error('MONGO_URI="mongodb+srv://user:pass@host/db" node scripts/check_mongo.js')
    process.exit(2)
  }

  const dbName = process.env.MONGO_DB || 'media_crawler'
  const collName = process.env.CREATOR_COLLECTION || 'xhs_users'

  const client = new MongoClient(uri, { useUnifiedTopology: true })
  try {
    await client.connect()
    const db = client.db(dbName)
    const coll = db.collection(collName)

    const count = await coll.countDocuments()
    console.log(`collection ${dbName}.${collName} count: ${count}`)

    const sample = await coll.find({}).limit(5).toArray()
    if (sample.length === 0) {
      console.log('no sample documents found')
    } else {
      console.log('sample docs (id, nickname, fans):')
      sample.forEach((d) => {
        const id = d._id?.toString()
        const nick = d.nickname || d.name || d.nick || ''
        const fans = d.fans || d.followers || 0
        console.log(`- ${id} | ${nick} | fans=${fans}`)
      })
    }
  } catch (err) {
    console.error('Error connecting to Mongo:', err && err.stack ? err.stack : err)
    process.exitCode = 1
  } finally {
    await client.close()
  }
}

main()
