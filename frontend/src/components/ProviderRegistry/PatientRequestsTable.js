import React, { useState } from 'react';
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Badge,
  Text,
  Box,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  VStack,
  Heading,
  Alert,
  AlertIcon,
  Flex,
  HStack,
  useToast
} from '@chakra-ui/react';
import { API_BASE_URL } from '../../config';

/**
 * Table component for displaying and managing patient provider requests
 */
const PatientRequestsTable = ({ patientRequests }) => {
  const [selectedRequest, setSelectedRequest] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Handle view details
  const handleViewDetails = (request) => {
    setSelectedRequest(request);
    onOpen();
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Handle creating a provider from patient request
  const handleCreateProviderFromRequest = async (requestId) => {
    try {
      // This would call the API to create a provider registration from the patient request
      const response = await fetch(
        `${API_BASE_URL}/api/provider-registry/admin/patient-request/${requestId}/create-provider`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to create provider from request');
      }
      
      toast({
        title: 'Provider created',
        description: 'A provider registration was created from the patient request',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      onClose();
    } catch (error) {
      toast({
        title: 'Error creating provider',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'yellow';
      case 'processed':
        return 'green';
      case 'rejected':
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <>
      {patientRequests.length === 0 ? (
        <Alert status="info">
          <AlertIcon />
          No patient provider requests found
        </Alert>
      ) : (
        <Box overflowX="auto">
          <Table variant="simple" size="md">
            <Thead>
              <Tr bg="gray.50">
                <Th>Requested Provider</Th>
                <Th>Type</Th>
                <Th>Patient</Th>
                <Th>Requested At</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {patientRequests.map((request) => (
                <Tr key={request.id} _hover={{ bg: 'gray.50' }}>
                  <Td fontWeight="medium">{request.provider_name}</Td>
                  <Td>
                    <Badge>
                      {request.provider_type.charAt(0).toUpperCase() + request.provider_type.slice(1)}
                    </Badge>
                  </Td>
                  <Td>{request.patient_id}</Td>
                  <Td>{formatDate(request.requested_at)}</Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(request.status)}>
                      {request.status.toUpperCase()}
                    </Badge>
                  </Td>
                  <Td>
                    <Button
                      size="sm"
                      colorScheme="blue"
                      variant="outline"
                      onClick={() => handleViewDetails(request)}
                    >
                      View Details
                    </Button>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}

      {/* Request Details Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader borderBottomWidth="1px">
            Patient Provider Request Details
          </ModalHeader>
          <ModalCloseButton />
          
          <ModalBody py={6}>
            {selectedRequest && (
              <VStack spacing={5} align="stretch">
                <Flex justify="space-between" align="center">
                  <Heading as="h3" size="md">{selectedRequest.provider_name}</Heading>
                  <Badge colorScheme={getStatusColor(selectedRequest.status)} fontSize="md" px={2} py={1}>
                    {selectedRequest.status.toUpperCase()}
                  </Badge>
                </Flex>
                
                <Box p={4} bg="gray.50" borderRadius="md">
                  <Text fontWeight="bold" mb={1}>Provider Type:</Text>
                  <Text>{selectedRequest.provider_type.charAt(0).toUpperCase() + selectedRequest.provider_type.slice(1)}</Text>
                  
                  {selectedRequest.provider_website && (
                    <>
                      <Text fontWeight="bold" mt={3} mb={1}>Website:</Text>
                      <Text color="blue.500">
                        <a href={selectedRequest.provider_website} target="_blank" rel="noopener noreferrer">
                          {selectedRequest.provider_website}
                        </a>
                      </Text>
                    </>
                  )}
                  
                  {selectedRequest.provider_location && (
                    <>
                      <Text fontWeight="bold" mt={3} mb={1}>Location:</Text>
                      <Text>{selectedRequest.provider_location}</Text>
                    </>
                  )}
                </Box>

                {selectedRequest.request_reason && (
                  <Box p={4} bg="blue.50" borderRadius="md">
                    <Heading as="h4" size="sm" mb={2}>Request Reason</Heading>
                    <Text>{selectedRequest.request_reason}</Text>
                  </Box>
                )}
                
                <Box p={4} borderRadius="md" borderWidth="1px">
                  <Heading as="h4" size="sm" mb={2}>Patient Information</Heading>
                  <Text>
                    <strong>Patient ID:</strong> {selectedRequest.patient_id}
                  </Text>
                  {selectedRequest.patient_email && (
                    <Text>
                      <strong>Email:</strong> {selectedRequest.patient_email}
                    </Text>
                  )}
                </Box>
                
                <Box p={4} bg="gray.100" borderRadius="md">
                  <Text fontSize="sm" color="gray.600">
                    <strong>Requested at:</strong> {formatDate(selectedRequest.requested_at)}
                  </Text>
                </Box>
              </VStack>
            )}
          </ModalBody>

          <ModalFooter borderTopWidth="1px">
            <HStack spacing={3}>
              <Button variant="ghost" onClick={onClose}>
                Close
              </Button>
              {selectedRequest && selectedRequest.status === 'pending' && (
                <Button 
                  colorScheme="blue"
                  onClick={() => handleCreateProviderFromRequest(selectedRequest.id)}
                >
                  Create Provider Registration
                </Button>
              )}
            </HStack>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default PatientRequestsTable;
