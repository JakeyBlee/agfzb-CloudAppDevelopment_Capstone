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
          db: 'reviews',
          includeDocs: true
        });
        let reviews = response.result.rows.map(row => ({
            id: row.doc.id,
            name: row.doc.name,
            dealership: row.doc.dealership,
            review: row.doc.review,
            purchase: row.doc.purchase,
            purchase_date: row.doc.purchase_date,
            car_make: row.doc.car_make,
            car_model: row.doc.car_model,
            car_year: row.doc.car_year
        }));
        const filteredReviews = reviews.filter(res => res.dealership == params.dealerId);
        if(filteredReviews.length == 0){
            throw new Error("404: dealerId does not exist");
        }
        return { body: filteredReviews };
      } catch (error) {
          return { body: { error: error.message }};
      }
}