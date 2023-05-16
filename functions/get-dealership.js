const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

async function main(params) {
      const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY })
      const cloudant = CloudantV1.newInstance({
          authenticator: authenticator
      });
      cloudant.setServiceUrl(params.COUCH_URL);
      try {
        let response = await cloudant.postAllDocs({
          db: 'dealerships',
          includeDocs: true
        });
        let dealerships = response.result.rows.map(row => ({
            id: row.doc.id,
            city: row.doc.city,
            state: row.doc.state,
            st: row.doc.st,
            address: row.doc.address,
            zip: row.doc.zip,
            lat: row.doc.lat,
            long: row.doc.long
        }));
        if(params.state){
            dealerships = dealerships.filter(res => res.st.toLowerCase() == params.state.toLowerCase())
            if(dealerships.length == 0 ) throw new Error("404: The state does not exist");
        };
        if(dealerships.length == 0 ) throw new Error("404: The database is empty");
        return { body: dealerships };
      } catch (error) {
          return {body: { error: error.message }};
      }
}