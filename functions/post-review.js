const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

async function main(params) {
      const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY })
      const cloudant = CloudantV1.newInstance({
          authenticator: authenticator
      });
      cloudant.setServiceUrl(params.COUCH_URL);
      try {
        const review = {
            id: params.id,
            name: params.name,
            dealership: params.dealership,
            review: params.review,
            purchase: params.purchase,
            another: params.another,
            purchase_date: params.purchase_date,
            car_make: params.car_make,
            car_model: params.car_model,
            car_year: params.car_year
        };
        let response = await cloudant.postDocument({
          db: 'reviews',
          document: review
        });
        return { body: response.result };
        
      } catch (error) {
          return { body: { error: error.message }};
      }
}