const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

async function main(params) {
      const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY })
      const cloudant = CloudantV1.newInstance({
          authenticator: authenticator
      });
      cloudant.setServiceUrl(params.COUCH_URL);
      try {
        const payload = params.__ow_body;
        const review = payload.review;
        let response = await cloudant.postDocument({
          db: 'reviews',
          document: review
        });
        return { body: response.result };
        
      } catch (error) {
          return { body: { error: error.message }};
      }
}